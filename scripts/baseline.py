"""Generate a trivial baseline submission for AIMO3."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
SUBMISSIONS = ROOT / "submissions"


def main() -> None:
    test = pd.read_csv(RAW / "test.csv")
    submission = test[["id"]].copy()
    submission["answer"] = 0
    SUBMISSIONS.mkdir(parents=True, exist_ok=True)
    out_path = SUBMISSIONS / "baseline.csv"
    submission.to_csv(out_path, index=False)
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
