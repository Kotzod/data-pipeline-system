import sqlite3
from datetime import date
import pandas as pd

DATABASE = "football_pipeline.db"


def get_current_season_start():

    today = date.today()
    start_year = today.year if today.month >= 8 else today.year - 1

    return date(start_year, 8, 1)

conn = sqlite3.connect(DATABASE)

tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table'", conn)
table_names = tables["name"].tolist()

if "matches" not in table_names:
    print("Table 'matches' not found in", DATABASE)
else:
    df = pd.read_sql("SELECT * FROM matches", conn)

    print("Rows:", len(df))
    print("Columns:", ", ".join(df.columns))

    if "match_date" in df.columns:
        df["match_date"] = pd.to_datetime(df["match_date"], errors="coerce")
        min_date = df["match_date"].min()
        max_date = df["match_date"].max()
        print("Date range:", min_date, "to", max_date)

        season_start = get_current_season_start()
        season_df = df[df["match_date"].dt.date >= season_start].copy()
        print("\nSeason analysis from", season_start, ":")
        print("Matches:", len(season_df))

        if not season_df.empty and {"home_goals", "away_goals"}.issubset(season_df.columns):
            total_goals = season_df["home_goals"] + season_df["away_goals"]
            print("Avg goals per match:", round(total_goals.mean(), 2))

        if not season_df.empty and {"home_win", "draw", "away_win"}.issubset(season_df.columns):
            home_rate = season_df["home_win"].mean()
            draw_rate = season_df["draw"].mean()
            away_rate = season_df["away_win"].mean()
            print(
                "Win rates (H/D/A):",
                round(home_rate, 3),
                round(draw_rate, 3),
                round(away_rate, 3)
            )

    if {"home_goals", "away_goals"}.issubset(df.columns):
        print("\nGoal summary:")
        goal_summary = df[["home_goals", "away_goals"]].describe()
        goal_summary = goal_summary.loc[["count", "mean", "std", "max"]]
        print(goal_summary)

    numeric_cols = df.select_dtypes(include="number").columns
    if len(numeric_cols) > 0:
        print("\nNumeric summary:")
        print(df[numeric_cols].describe())

    display_cols = [
        col for col in [
            "match_date",
            "home_team",
            "away_team",
            "home_goals",
            "away_goals"
        ] if col in df.columns
    ]

    if display_cols:
        print("\nMost recent matches:")
        recent = df.sort_values("match_date", ascending=False).head(20)
        print(recent[display_cols].to_string(index=False))

conn.close()