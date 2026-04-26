"""ML helpers: CLV (Linear Regression), Basket Analysis (association rules),
Churn Prediction (Logistic Regression / Gradient Boosting)."""
from collections import Counter, defaultdict
from itertools import combinations

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestRegressor
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, accuracy_score


def compute_clv(tx_df: pd.DataFrame):
    """Predict Customer Lifetime Value using Linear Regression.
    Features: basket_count, avg_basket_value, units, distinct_products.
    Target: total spend (proxy for CLV over the 2-year window)."""
    g = tx_df.groupby("HSHD_NUM").agg(
        basket_count=("BASKET_NUM", "nunique"),
        total_units=("UNITS", "sum"),
        distinct_products=("PRODUCT_NUM", "nunique"),
        avg_spend=("SPEND", "mean"),
        total_spend=("SPEND", "sum"),
    ).reset_index()

    if len(g) < 10:
        return {"error": "not enough households"}

    X = g[["basket_count", "total_units", "distinct_products", "avg_spend"]].values
    y = g["total_spend"].values
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42)

    lr = LinearRegression().fit(Xtr, ytr)
    rf = RandomForestRegressor(n_estimators=50, random_state=42).fit(Xtr, ytr)

    g["predicted_clv"] = lr.predict(X)
    top = g.sort_values("predicted_clv", ascending=False).head(20)

    return {
        "model": "LinearRegression (baseline) + RandomForest (comparison)",
        "linear_r2": float(r2_score(yte, lr.predict(Xte))),
        "rf_r2": float(r2_score(yte, rf.predict(Xte))),
        "feature_importance": dict(zip(
            ["basket_count", "total_units", "distinct_products", "avg_spend"],
            [float(c) for c in lr.coef_],
        )),
        "top_high_value_households": top[["HSHD_NUM", "predicted_clv", "total_spend"]]
            .to_dict(orient="records"),
    }


def basket_association(tx_df: pd.DataFrame, min_support: int = 5, top_n: int = 15):
    """Market-basket association rules via co-occurrence + lift.
    Uses commodity-level baskets; computes support, confidence, lift."""
    baskets = tx_df.groupby("BASKET_NUM")["COMMODITY"].apply(
        lambda s: list(set(s.dropna()))
    )
    n_baskets = len(baskets)
    if n_baskets == 0:
        return {"error": "no baskets"}

    item_counts = Counter()
    pair_counts = Counter()
    for items in baskets:
        for it in items:
            item_counts[it] += 1
        for a, b in combinations(sorted(items), 2):
            pair_counts[(a, b)] += 1

    rules = []
    for (a, b), cnt in pair_counts.items():
        if cnt < min_support:
            continue
        support = cnt / n_baskets
        conf_ab = cnt / item_counts[a]
        conf_ba = cnt / item_counts[b]
        lift = (cnt * n_baskets) / (item_counts[a] * item_counts[b])
        rules.append({
            "item_a": a, "item_b": b,
            "support": round(support, 4),
            "confidence_a_to_b": round(conf_ab, 4),
            "confidence_b_to_a": round(conf_ba, 4),
            "lift": round(lift, 3),
            "co_purchase_count": cnt,
        })
    rules.sort(key=lambda r: r["lift"], reverse=True)
    return {
        "method": "Association rule mining (support / confidence / lift)",
        "n_baskets": n_baskets,
        "top_rules": rules[:top_n],
    }


def churn_predict(tx_df: pd.DataFrame):
    """Churn prediction with Gradient Boosting + Logistic Regression.
    Label: household is 'churned' if no purchase in last 90 days of dataset."""
    tx_df = tx_df.copy()
    tx_df["DATE"] = pd.to_datetime(tx_df["DATE"], errors="coerce")
    tx_df = tx_df.dropna(subset=["DATE"])

    cutoff = tx_df["DATE"].max() - pd.Timedelta(days=90)

    g = tx_df.groupby("HSHD_NUM").agg(
        basket_count=("BASKET_NUM", "nunique"),
        total_spend=("SPEND", "sum"),
        avg_spend=("SPEND", "mean"),
        total_units=("UNITS", "sum"),
        last_purchase=("DATE", "max"),
        first_purchase=("DATE", "min"),
    ).reset_index()
    g["tenure_days"] = (g["last_purchase"] - g["first_purchase"]).dt.days
    g["churned"] = (g["last_purchase"] < cutoff).astype(int)

    if g["churned"].nunique() < 2 or len(g) < 20:
        return {"error": "not enough class variation"}

    feats = ["basket_count", "total_spend", "avg_spend", "total_units", "tenure_days"]
    X = g[feats].fillna(0).values
    y = g["churned"].values
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    gb = GradientBoostingClassifier(random_state=42).fit(Xtr, ytr)
    lr = LogisticRegression(max_iter=500).fit(Xtr, ytr)

    g["churn_probability"] = gb.predict_proba(X)[:, 1]
    at_risk = g.sort_values("churn_probability", ascending=False).head(20)

    return {
        "model": "GradientBoostingClassifier (primary) + LogisticRegression (baseline)",
        "gb_accuracy": float(accuracy_score(yte, gb.predict(Xte))),
        "lr_accuracy": float(accuracy_score(yte, lr.predict(Xte))),
        "feature_importance": dict(zip(feats, [float(v) for v in gb.feature_importances_])),
        "churn_rate": float(g["churned"].mean()),
        "top_at_risk_households": at_risk[
            ["HSHD_NUM", "churn_probability", "total_spend", "basket_count"]
        ].to_dict(orient="records"),
    }
