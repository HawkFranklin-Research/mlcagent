"""Synthetic 400-row binary classification table used by the reviewer's smoke run (seed 0)."""

import sys

import numpy as np
import pandas as pd

rng = np.random.default_rng(0)
n = 400
X = rng.normal(size=(n, 4))
y = (X[:, 0] + 0.5 * X[:, 1] + rng.normal(size=n) > 0).astype(int)
frame = pd.DataFrame(X, columns=["x1", "x2", "x3", "x4"])
frame["y"] = y
frame.to_csv(sys.argv[1] if len(sys.argv) > 1 else "synth.csv", index=False)
