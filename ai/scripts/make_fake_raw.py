"""Fake CSVs with the SAME schema as the Kaggle aquaponics dataset — only to smoke-test the code."""
import sys, numpy as np, pandas as pd
from pathlib import Path
out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
rng = np.random.default_rng(0)
for p in range(1, 4):
    t = pd.date_range("2021-06-19", periods=6 * 24 * 7, freq="10min")
    h = t.hour + t.minute / 60
    do = 6 + 1.8 * np.sin(2 * np.pi * (h - 9) / 24) + rng.normal(0, .25, len(t))
    df = pd.DataFrame({"created_at": t.strftime("%Y-%m-%d %H:%M:%S UTC"), "entry_id": range(len(t)),
        "Temperature (C)": 26 + 1.5 * np.sin(2 * np.pi * (h - 14) / 24) + rng.normal(0, .1, len(t)),
        "Turbidity(NTU)": rng.normal(80, 5, len(t)), "Dissolved Oxygen(g/ml)": do,
        "PH": 7.4 + .3 * np.sin(2 * np.pi * (h - 15) / 24) + rng.normal(0, .05, len(t)),
        "Ammonia(g/ml)": rng.normal(.4, .05, len(t)), "Nitrate(g/ml)": rng.normal(300, 20, len(t)),
        "Population": 50, "Fish_Length(cm)": 7.1, "Fish_Weight(g)": 2.9})
    df.to_csv(out / f"IoT_pond{p}.csv", index=False)
