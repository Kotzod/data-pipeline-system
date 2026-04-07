import logging
import os
import requests
import pandas as pd
import numpy as np
import sqlite3
import time
from datetime import date, timedelta
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from scipy.stats import poisson

# Config

logging.basicConfig(
    filename="pipeline.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def load_env(path=".env"):

    if not os.path.exists(path):
        return

    with open(path, "r", encoding="utf-8") as env_file:
        for line in env_file:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip("\"").strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


load_env()

FOOTBALL_DATA_KEY = os.getenv("FOOTBALL_DATA_KEY", "")
API_FOOTBALL_KEY = os.getenv("API_FOOTBALL_KEY", "")

HEADERS1 = {"X-Auth-Token": FOOTBALL_DATA_KEY}
HEADERS2 = {"x-apisports-key": API_FOOTBALL_KEY}

MATCH_URL = "https://api.football-data.org/v4/competitions/PL/matches"
API_FOOTBALL_BASE_URL = "https://v3.football.api-sports.io"
API_FOOTBALL_FIXTURES_URL = f"{API_FOOTBALL_BASE_URL}/fixtures"
API_FOOTBALL_LEAGUE_ID = 39

DATABASE = "football_pipeline.db"
PREDICTIONS_DATABASE = "predictions.db"

PREDICTION_COLUMNS = [
    "match_date",
    "home_team",
    "away_team",
    "xg_home",
    "xg_away",
    "pred_home_goals",
    "pred_away_goals",
    "home_win_prob",
    "draw_prob",
    "away_win_prob",
    "predicted_outcome"
]

API_TIMEOUT = 30
SEASONS_BACK = 1
FUTURE_FIXTURE_COUNT = 60
FUTURE_DATE_RANGE_DAYS = 60


# Retry function

def fetch_with_retry(url, headers=None, params=None, retries=3):

    for _ in range(retries):
        try:
            r = requests.get(url, headers=headers, params=params, timeout=API_TIMEOUT)
            if r.status_code == 200:
                return r.json()
            logging.warning("API returned status %s for %s", r.status_code, url)
        except:
            pass

        logging.warning("Retrying API request to %s", url)
        print("Retrying API...")
        time.sleep(3)

    logging.error("API failure for %s", url)
    raise Exception("API failure")


def require_api_keys():

    missing = []
    if not FOOTBALL_DATA_KEY:
        missing.append("FOOTBALL_DATA_KEY")
    if not API_FOOTBALL_KEY:
        missing.append("API_FOOTBALL_KEY")
    if missing:
        logging.error("Missing API keys: %s", ", ".join(missing))
        raise RuntimeError(
            "Missing API keys: "
            + ", ".join(missing)
            + ". Set them in .env or environment variables."
        )


# Fetch match data

def get_recent_seasons(years_back=1):

    today = date.today()
    current_start = today.year if today.month >= 8 else today.year - 1

    return [current_start - i for i in range(years_back, -1, -1)]


def get_current_season_start():

    today = date.today()

    return today.year if today.month >= 8 else today.year - 1


def fetch_matches_football_data(seasons):

    matches = []

    for season in seasons:
        data = fetch_with_retry(MATCH_URL, HEADERS1, params={"season": season})

        for m in data.get("matches", []):

            if m["score"]["fullTime"]["home"] is None:
                continue

            match_date = m.get("utcDate", "")[:10]

            matches.append({
                "match_date": match_date,
                "home_team": m["homeTeam"]["name"],
                "away_team": m["awayTeam"]["name"],
                "home_goals": m["score"]["fullTime"]["home"],
                "away_goals": m["score"]["fullTime"]["away"]
            })

    logging.info("Fetched %s matches from football-data", len(matches))

    return pd.DataFrame(matches)


def fetch_matches_api_football(seasons):

    matches = []

    for season in seasons:
        data = fetch_with_retry(
            API_FOOTBALL_FIXTURES_URL,
            HEADERS2,
            params={
                "league": API_FOOTBALL_LEAGUE_ID,
                "season": season,
                "status": "FT-AET-PEN"
            }
        )

        for m in data.get("response", []):
            fixture = m.get("fixture", {})
            teams = m.get("teams", {})
            goals = m.get("goals", {})

            home_goals = goals.get("home")
            away_goals = goals.get("away")

            if home_goals is None or away_goals is None:
                continue

            match_date = fixture.get("date", "")[:10]
            home_team = teams.get("home", {}).get("name")
            away_team = teams.get("away", {}).get("name")

            if not home_team or not away_team:
                continue

            matches.append({
                "match_date": match_date,
                "home_team": home_team,
                "away_team": away_team,
                "home_goals": home_goals,
                "away_goals": away_goals
            })

    logging.info("Fetched %s matches from API-Football", len(matches))

    return pd.DataFrame(matches)


def fetch_matches(seasons=None):

    if seasons is None:
        seasons = get_recent_seasons(SEASONS_BACK)

    fd_matches = fetch_matches_football_data(seasons)
    api_matches = fetch_matches_api_football(seasons)

    if fd_matches.empty:
        return api_matches
    if api_matches.empty:
        return fd_matches

    combined = pd.concat([fd_matches, api_matches], ignore_index=True)
    combined = combined.drop_duplicates(
        subset=["match_date", "home_team", "away_team"]
    ).reset_index(drop=True)

    logging.info("Combined match count: %s", len(combined))

    return combined


def fetch_upcoming_fixtures(count=10):

    season = get_current_season_start()
    fixtures = []
    seen = set()

    def add_fixture(match_date, home_team, away_team):
        if not match_date or not home_team or not away_team:
            return

        key = (match_date[:10], home_team, away_team)
        if key in seen:
            return

        seen.add(key)
        fixtures.append({
            "match_date": match_date,
            "home_team": home_team,
            "away_team": away_team
        })

    data = fetch_with_retry(
        API_FOOTBALL_FIXTURES_URL,
        HEADERS2,
        params={
            "league": API_FOOTBALL_LEAGUE_ID,
            "season": season,
            "status": "NS",
            "next": count
        }
    )

    if not data.get("response"):
        data = fetch_with_retry(
            API_FOOTBALL_FIXTURES_URL,
            HEADERS2,
            params={
                "league": API_FOOTBALL_LEAGUE_ID,
                "season": season,
                "next": count
            }
        )

    for m in data.get("response", []):
        fixture = m.get("fixture", {})
        teams = m.get("teams", {})

        home_team = teams.get("home", {}).get("name")
        away_team = teams.get("away", {}).get("name")

        match_date = fixture.get("date", "")
        add_fixture(match_date, home_team, away_team)

    if len(fixtures) < count:
        logging.info(
            "Using football-data fallback for upcoming fixtures (%s/%s)",
            len(fixtures),
            count
        )
        date_from = date.today()
        date_to = date_from + timedelta(days=FUTURE_DATE_RANGE_DAYS)

        fallback = fetch_with_retry(
            MATCH_URL,
            HEADERS1,
            params={
                "dateFrom": date_from.isoformat(),
                "dateTo": date_to.isoformat(),
                "status": "SCHEDULED"
            }
        )

        for m in fallback.get("matches", []):
            match_date = m.get("utcDate", "")
            home_team = m.get("homeTeam", {}).get("name")
            away_team = m.get("awayTeam", {}).get("name")
            add_fixture(match_date, home_team, away_team)

    fixtures = sorted(fixtures, key=lambda item: item["match_date"])[:count]

    logging.info("Upcoming fixtures fetched: %s", len(fixtures))

    return fixtures


# Validate data

def validate_data(df):

    df = df.dropna()

    df = df[(df.home_goals >= 0) & (df.away_goals >= 0)]

    df["home_goals"] = df["home_goals"].astype(int)
    df["away_goals"] = df["away_goals"].astype(int)

    return df


# Feature engineering

def create_features(df):

    df["home_win"] = (df.home_goals > df.away_goals).astype(int)

    df["draw"] = (df.home_goals == df.away_goals).astype(int)

    df["away_win"] = (df.away_goals > df.home_goals).astype(int)

    return df


# Expected goals (team strength model)

def calculate_team_strengths(df):

    league_avg_home = df.home_goals.mean()
    league_avg_away = df.away_goals.mean()

    home_stats = df.groupby("home_team").agg(
        home_goals_for=("home_goals", "mean"),
        home_goals_against=("away_goals", "mean")
    )

    away_stats = df.groupby("away_team").agg(
        away_goals_for=("away_goals", "mean"),
        away_goals_against=("home_goals", "mean")
    )

    teams = sorted(set(df.home_team) | set(df.away_team))
    strengths = pd.DataFrame(index=teams)
    strengths["home_attack"] = home_stats["home_goals_for"] / league_avg_home
    strengths["home_defense"] = home_stats["home_goals_against"] / league_avg_away
    strengths["away_attack"] = away_stats["away_goals_for"] / league_avg_away
    strengths["away_defense"] = away_stats["away_goals_against"] / league_avg_home

    strengths = strengths.fillna(1.0)

    return strengths, {"home": league_avg_home, "away": league_avg_away}


def calculate_expected_goals(df):

    strengths, league_avgs = calculate_team_strengths(df)

    df = df.copy()
    df["home_attack"] = df["home_team"].map(strengths["home_attack"]).fillna(1.0)
    df["away_attack"] = df["away_team"].map(strengths["away_attack"]).fillna(1.0)
    df["home_defense"] = df["home_team"].map(strengths["home_defense"]).fillna(1.0)
    df["away_defense"] = df["away_team"].map(strengths["away_defense"]).fillna(1.0)

    df["xg_home"] = league_avgs["home"] * df["home_attack"] * df["away_defense"]
    df["xg_away"] = league_avgs["away"] * df["away_attack"] * df["home_defense"]

    return df, strengths, league_avgs


# Poisson goal model

def poisson_prediction(home_lambda, away_lambda, max_goals=10):

    goals = np.arange(0, max_goals + 1)
    home_probs = poisson.pmf(goals, home_lambda)
    away_probs = poisson.pmf(goals, away_lambda)
    matrix = np.outer(home_probs, away_probs)

    home_win = np.sum(np.tril(matrix, -1))
    draw = np.sum(np.diag(matrix))
    away_win = np.sum(np.triu(matrix, 1))

    return home_win, draw, away_win


def most_likely_scoreline(home_lambda, away_lambda, max_goals=10):

    goals = np.arange(0, max_goals + 1)
    home_probs = poisson.pmf(goals, home_lambda)
    away_probs = poisson.pmf(goals, away_lambda)
    matrix = np.outer(home_probs, away_probs)

    max_index = np.unravel_index(np.argmax(matrix), matrix.shape)

    return int(max_index[0]), int(max_index[1])


# Database storage

def store_database(df):

    conn = sqlite3.connect(DATABASE)

    df.to_sql("matches", conn, if_exists="replace", index=False)
    logging.info("Saved %s rows to matches table", len(df))
    if "match_date" in df.columns:
        season_start_date = date(get_current_season_start(), 8, 1)
        season_df = df.copy()
        season_df["match_date"] = pd.to_datetime(
            season_df["match_date"],
            errors="coerce"
        ).dt.date
        season_df = season_df[season_df["match_date"] >= season_start_date]
        season_df.to_sql("season_matches", conn, if_exists="replace", index=False)
        logging.info("Saved %s rows to season_matches table", len(season_df))
    conn.execute("DROP TABLE IF EXISTS predictions")

    conn.close()


def store_predictions(df, as_of_date):

    df = df.copy()
    if "match_date" not in df.columns:
        df["match_date"] = pd.Series(dtype="string")

    match_day = pd.to_datetime(
        df["match_date"].astype(str).str.slice(0, 10),
        errors="coerce"
    ).dt.date
    future_df = df[match_day >= as_of_date].copy()

    conn = sqlite3.connect(PREDICTIONS_DATABASE)
    future_df.to_sql("predictions", conn, if_exists="replace", index=False)
    conn.close()
    logging.info("Saved %s rows to predictions.db", len(future_df))


# Machine learning model

def train_model(df):

    feature_cols = [
        "xg_home",
        "xg_away",
        "home_attack",
        "away_attack",
        "home_defense",
        "away_defense"
    ]

    features = df[feature_cols]

    target = df["home_win"]

    X_train, X_test, y_train, y_test = train_test_split(
        features,
        target,
        test_size=0.2,
        random_state=42
    )

    model = RandomForestClassifier(
        n_estimators=400,
        max_depth=12
    )

    model.fit(X_train, y_train)

    preds = model.predict(X_test)

    accuracy = accuracy_score(y_test, preds)

    print("Model Accuracy:", accuracy)

    return model, feature_cols


# Win probability calculation

def win_probability(home_lambda, away_lambda):

    home, draw, away = poisson_prediction(home_lambda, away_lambda)

    total = home + draw + away

    return {
        "home_win_prob": home / total,
        "draw_prob": draw / total,
        "away_win_prob": away / total
    }


def pick_outcome(probs):

    return max(
        [
            ("Home", probs["home_win_prob"]),
            ("Draw", probs["draw_prob"]),
            ("Away", probs["away_win_prob"])
        ],
        key=lambda item: item[1]
    )[0]


# Upcoming match prediction

def predict_match(home_team, away_team, model, strengths, league_avgs, feature_cols):

    if home_team in strengths.index:
        home_strength = strengths.loc[home_team]
    else:
        home_strength = pd.Series({
            "home_attack": 1.0,
            "away_attack": 1.0,
            "home_defense": 1.0,
            "away_defense": 1.0
        })

    if away_team in strengths.index:
        away_strength = strengths.loc[away_team]
    else:
        away_strength = pd.Series({
            "home_attack": 1.0,
            "away_attack": 1.0,
            "home_defense": 1.0,
            "away_defense": 1.0
        })

    home_xg = league_avgs["home"] * home_strength["home_attack"] * away_strength["away_defense"]
    away_xg = league_avgs["away"] * away_strength["away_attack"] * home_strength["home_defense"]

    probs = win_probability(home_xg, away_xg)

    features = pd.DataFrame([{
        "xg_home": home_xg,
        "xg_away": away_xg,
        "home_attack": home_strength["home_attack"],
        "away_attack": away_strength["away_attack"],
        "home_defense": home_strength["home_defense"],
        "away_defense": away_strength["away_defense"]
    }])

    features = features[feature_cols]

    prediction = model.predict(features)[0]

    return prediction, probs, home_xg, away_xg


# Main pipeline

def run_pipeline():

    require_api_keys()

    logging.info("Fetching match data")
    print("Fetching match data...")

    matches = fetch_matches()

    logging.info("Validating data")
    print("Validating...")
    matches.loc[0, "home_goals"] = None

    matches = validate_data(matches)

    logging.info("Creating features")
    print("Creating features...")

    matches = create_features(matches)

    logging.info("Calculating xG")
    print("Calculating xG...")

    matches, strengths, league_avgs = calculate_expected_goals(matches)

    logging.info("Saving to database")
    print("Saving to database...")

    store_database(matches)

    logging.info("Training ML model")
    print("Training ML model...")

    model, feature_cols = train_model(matches)

    logging.info("Predicting example match")
    print("Predicting example match...")

    pred, probs, _, _ = predict_match(
        "Manchester City",
        "Arsenal",
        model,
        strengths,
        league_avgs,
        feature_cols
    )

    print("\nPrediction:")
    print("Home Win Probability:", round(probs["home_win_prob"], 3))
    print("Draw Probability:", round(probs["draw_prob"], 3))
    print("Away Win Probability:", round(probs["away_win_prob"], 3))

    if pred == 1:
        print("Predicted Winner: Home Team")
    else:
        print("Predicted Winner: Away Team")

    logging.info("Predicting upcoming fixtures")
    print("\nNext 10 Premier League fixtures:")

    upcoming = fetch_upcoming_fixtures(FUTURE_FIXTURE_COUNT)

    predictions = []
    today_local = date.today()

    for index, fixture in enumerate(upcoming):
        home_team = fixture["home_team"]
        away_team = fixture["away_team"]
        match_date = fixture["match_date"].replace("T", " ")[:16]

        _, probs, home_xg, away_xg = predict_match(
            home_team,
            away_team,
            model,
            strengths,
            league_avgs,
            feature_cols
        )

        outcome = pick_outcome(probs)
        pred_home_goals, pred_away_goals = most_likely_scoreline(home_xg, away_xg)

        predictions.append({
            "match_date": fixture["match_date"],
            "home_team": home_team,
            "away_team": away_team,
            "xg_home": home_xg,
            "xg_away": away_xg,
            "pred_home_goals": pred_home_goals,
            "pred_away_goals": pred_away_goals,
            "home_win_prob": probs["home_win_prob"],
            "draw_prob": probs["draw_prob"],
            "away_win_prob": probs["away_win_prob"],
            "predicted_outcome": outcome
        })

        if index < 10:
            print(f"{match_date} - {home_team} vs {away_team}")
            print(
                "Predicted:",
                outcome,
                "| H:",
                round(probs["home_win_prob"], 3),
                "D:",
                round(probs["draw_prob"], 3),
                "A:",
                round(probs["away_win_prob"], 3)
            )
            print(
                "Expected Goals:",
                round(home_xg, 2),
                "-",
                round(away_xg, 2),
                "| Scoreline:",
                f"{pred_home_goals}-{pred_away_goals}"
            )

    predictions_df = pd.DataFrame(predictions, columns=PREDICTION_COLUMNS)
    store_predictions(predictions_df, today_local)


if __name__ == "__main__":
    try:
        logging.info("Pipeline started")
        run_pipeline()
        logging.info("Pipeline finished successfully")
    except Exception as e:
        logging.error("Pipeline failed: %s", e)
        print("Pipeline failed. Check pipeline.log for details.")