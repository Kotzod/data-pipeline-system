import os
import sqlite3
import pandas as pd
from datetime import date

DATABASE = "predictions.db"

if not os.path.exists(DATABASE):
    print("Predictions database not found. Run main.py to generate", DATABASE)
    raise SystemExit(0)

conn = sqlite3.connect(DATABASE)

tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table'", conn)
table_names = tables["name"].tolist()

if "predictions" not in table_names:
    print("Table 'predictions' not found in", DATABASE)
else:
    preds = pd.read_sql("SELECT * FROM predictions", conn)
    print("Rows:", len(preds))
    print("Columns:", ", ".join(preds.columns))

    if "match_date" in preds.columns:
        preds["match_day"] = pd.to_datetime(
            preds["match_date"].astype(str).str.slice(0, 10),
            errors="coerce"
        ).dt.date

    today = date.today()
    if "match_day" in preds.columns:
        preds = preds[preds["match_day"] >= today].copy()

    pred_cols = [
        col for col in [
            "match_date",
            "home_team",
            "away_team",
            "predicted_outcome",
            "xg_home",
            "xg_away",
            "pred_home_goals",
            "pred_away_goals",
            "home_win_prob",
            "draw_prob",
            "away_win_prob"
        ] if col in preds.columns
    ]

    if pred_cols and not preds.empty:
        if "match_date" in pred_cols:
            match_dt = pd.to_datetime(
                preds["match_date"].astype(str).str.slice(0, 10),
                errors="coerce"
            )
            preds["match_date"] = match_dt.dt.strftime("%d-%m-%Y")

        print("\nUpcoming predictions:")
        latest = preds.sort_values("match_date", ascending=True).head(50)
        print(latest[pred_cols].to_string(index=False))
    else:
        print("\nNo future predictions found in", DATABASE)

conn.close()
