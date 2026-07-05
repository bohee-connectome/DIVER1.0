#!/usr/bin/env python3
"""
Recover multiclass auc_pr / AUROC for EEGPT linear-probe runs — post-hoc, no retraining.

WHY
  EEGPT eval (pyhealth `multiclass_metrics_fn` via `utils_eval.get_metrics`) only emits
  acc / balanced_acc / cohen_kappa / f1 for multi-class datasets. Its else-branch metrics
  list has no AUC (only the binary branch has pr_auc / roc_auc). ADFTD and CAUEEG are both
  3-class, so auc_pr / AUROC are silently absent from every run.

  Recovery is EXACT because the best checkpoint (save_top_k=1) per seed is saved on disk:
  reload it, re-run test only, dump softmax probabilities, then compute the AUCs offline.
  Reproducing the original ACC is the validation gate — if ACC does not match, stop.

STEP 1 — patch EEGPT/downstream/linear_probe_ours_5seeds.py (server, one-time):
  * add argparse flag:  parser.add_argument('--eval_only', action='store_true')
  * in the per-seed loop, replace the fit+test block with:
        import glob as _glob
        if args.eval_only:
            _ck = sorted(_glob.glob(os.path.join(seed_log_dir,'checkpoints','eegpt-epoch=*.ckpt')))
            _best = _ck[-1] if _ck else os.path.join(seed_log_dir,'checkpoints','last.ckpt')
            test_results = trainer.test(model, test_loader, ckpt_path=_best)[0]
        else:
            trainer.fit(model, train_loader, val_loader)
            test_results = trainer.test(model, test_loader, ckpt_path='best')[0]
        # dump test probs for offline AUC
        import numpy as _np
        _lab = torch.cat([a for a,_ in model.running_scores['test']]).cpu().numpy()
        _log = torch.cat([b for _,b in model.running_scores['test']]).cpu().float()
        _np.savez(os.path.join(seed_log_dir,'test_preds.npz'),
                  probs=torch.softmax(_log,dim=1).numpy(), labels=_lab)

STEP 2 — re-run test only (compute node; inference, short):
    module load pytorch/2.8.0
    python linear_probe_ours_5seeds.py --dataset CAUEEG --eval_only

STEP 3 — this script (login node, CPU):
    python recover_multiclass_auc.py \
        --logdir /pscratch/sd/b/boheelee/EEGPT/downstream/logs/linear_probe/CAUEEG \
        --seeds 1 42 123 777 3407 --expect_acc 0.5222

RESULT (CAUEEG EEGPT, 2026-07-05): auc_pr 0.543 +/- 0.011, AUROC 0.712 +/- 0.007
  (macro-OvR, ddof=0; ACC 0.5222 reproduced exactly). The dumped test_preds.npz stay on
  disk, so a different averaging convention can be recomputed without re-running anything.
"""
import argparse
import os

import numpy as np
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.preprocessing import label_binarize


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--logdir", required=True,
                    help="dir containing seed_<N>/test_preds.npz")
    ap.add_argument("--seeds", type=int, nargs="+", default=[1, 42, 123, 777, 3407])
    ap.add_argument("--expect_acc", type=float, default=None,
                    help="original run ACC for the reproduction gate")
    ap.add_argument("--ddof", type=int, default=0,
                    help="std ddof (0 matches linear_probe_ours_5seeds aggregation)")
    args = ap.parse_args()

    accs, praucs, aurocs = [], [], []
    for sd in args.seeds:
        fp = os.path.join(args.logdir, "seed_%d" % sd, "test_preds.npz")
        d = np.load(fp)
        p, y = d["probs"], d["labels"].astype(int)
        C = p.shape[1]
        Yb = label_binarize(y, classes=list(range(C)))
        acc = float((p.argmax(1) == y).mean())
        auroc = float(roc_auc_score(y, p, multi_class="ovr", average="macro"))
        prauc = float(average_precision_score(Yb, p, average="macro"))
        accs.append(acc); aurocs.append(auroc); praucs.append(prauc)
        print("seed %-5d N=%d  acc=%.4f  auc_pr=%.4f  auroc=%.4f"
              % (sd, len(y), acc, prauc, auroc))

    def ms(x):
        return "%.3f +/- %.3f" % (np.mean(x), np.std(x, ddof=args.ddof))

    print("=" * 52)
    print("ACC    : %s" % ms(accs))
    print("auc_pr : %s   (macro-OvR)" % ms(praucs))
    print("AUROC  : %s   (macro-OvR)" % ms(aurocs))
    if args.expect_acc is not None:
        ok = abs(np.mean(accs) - args.expect_acc) < 1e-3
        print("[check] ACC mean %.4f vs expected %.4f -> %s"
              % (np.mean(accs), args.expect_acc, "MATCH" if ok else "MISMATCH!"))


if __name__ == "__main__":
    main()
