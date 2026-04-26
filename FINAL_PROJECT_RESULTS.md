# Final Project Results — Retail Analytics on Azure
**Course:** Data Science and Analytics Using Azure Cloud Computing Technologies
**Dataset:** 8451 / Kroger — *The Complete Journey 2 Sample* (400 households, 2 years of transactions)
**Live Web App:** https://wonderful-desert-05af0470f.7.azurestaticapps.net
**Backend API:** https://retail-fastapi-ss-acgxdhamh2dybjeg.eastus2-01.azurewebsites.net
**Backend Repo:** https://github.com/nagarisn/CloudFinalProject
**Frontend Repo:** https://github.com/nagarisn/CloudFinalProject_Frontend

---

## Architecture Overview
- **Azure SQL Database** — stores `households`, `transactions`, `products` tables loaded from the provided CSVs.
- **Azure App Service (Linux, Python)** — hosts a FastAPI backend exposing data and ML endpoints.
- **Azure Static Web Apps** — hosts the HTML / CSS / JS frontend, auto-deployed via GitHub Actions.
- **GitHub Actions** — CI/CD for both repos.

```
[ Browser ] --> [ Azure Static Web Apps (frontend) ]
                        |
                        v
         [ Azure App Service (FastAPI backend) ]
                        |
                        v
              [ Azure SQL Database ]
```

---

## Requirement #1 — ML Models Write-Up (≤200 words)

**Linear Regression** fits a weighted linear combination of features to a continuous target by minimizing squared error. It is fast, fully interpretable through its coefficients, and an excellent baseline. Its main limitation is that it assumes a linear, additive relationship and underfits when interactions or non-linearities dominate.

**Random Forest** is an ensemble of decision trees, each trained on a bootstrap sample of rows and a random subset of features; predictions are averaged (regression) or voted (classification). It captures non-linearities and interactions automatically, is robust to outliers, and provides feature-importance scores. It costs more memory than a single tree and is harder to interpret.

**Gradient Boosting** builds trees sequentially, each new tree fit to the residual errors of the previous ensemble using gradient descent on a loss function. It usually achieves the best accuracy on tabular data but is sensitive to learning rate and depth and can overfit without regularization or early stopping.

**Selected for CLV:** Linear Regression (interpretable coefficients on basket count, units, distinct products, average spend) with a Random Forest comparison reported via R². Implemented in `ml_models.compute_clv` and exposed at `GET /ml/clv`.

---

## Requirement #2 — Web Server Setup
- FastAPI deployed to Azure App Service.
- Frontend has `index.html` (login), `register.html` (Username / Email / Password), and `portal.html` (post-login landing).
- Auth is client-side (`localStorage`) for demo simplicity.

## Requirement #3 — Datastore and Data Loading
- Azure SQL Database holds `households`, `transactions`, `products`.
- `GET /household/{hshd_num}` joins the three tables, sorted by **Hshd_num, Basket_num, Date, Product_num, Department, Commodity**.
- A "Sample Data Pull" page lets a user view results for **HSHD_NUM #10**.

## Requirement #4 — Interactive Search Page
- `search.html` lets a user enter any `Hshd_num`; the backend returns the same joined / sorted result.

## Requirement #5 — Data Loading Web App
- `upload.html` posts CSV files to `POST /upload-data`; updated data flows through the same search & dashboard endpoints.

## Requirement #6 — Dashboard
`dashboard.html` provides:
- Per-household KPIs (total spend, baskets, items, average spend, units)
- Top 5 commodities (bar chart)
- Basket popularity (pie chart)
- Churn risk distribution (bar chart)

## Requirement #7 — Basket Analysis (ML)
**Endpoint:** `GET /ml/basket`
**Method:** Association rule mining over commodity-level baskets — computes **support, confidence, and lift**.
**Insight:** Pairs with `lift > 1` are bought together more often than independence would predict; surface these as cross-sell candidates (e.g., bundled promotions, store-shelf adjacency, "frequently bought together" recommendations).

## Requirement #8 — Churn Prediction
**Endpoint:** `GET /ml/churn`
**Method:** **Gradient Boosting Classifier** (primary) + **Logistic Regression** (baseline).
**Label:** Household is "churned" if it has no purchase in the last 90 days of the dataset window.
**Features:** basket count, total spend, average spend, total units, tenure days.
**Output:** Per-household churn probability, model accuracy, feature importance, and a ranked list of the top at-risk households.
**Retention strategy:** Target the top-decile churn-probability households with personalized offers in their highest-spend commodities (read from `/top-products/{hshd_num}`).

---

## Bonus — Customer Lifetime Value (CLV)
**Endpoint:** `GET /ml/clv`
**Method:** Linear Regression baseline + Random Forest comparison; reports R² for both. Predicted CLV is used to rank households for high-value targeting.

---

## Team Contributions
- Backend, Azure SQL, App Service, ML pipeline, write-up
- Frontend, Static Web Apps deployment, dashboard charts, UI polish
