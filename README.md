# CloudFinalProject — Retail Analytics Backend

FastAPI backend for the 8451 / Kroger retail analytics project. Hosted on Azure App Service. Connects to an Azure SQL database containing households, transactions, and products tables.

- **Live API:** https://retail-fastapi-ss-acgxdhamh2dybjeg.eastus2-01.azurewebsites.net
- **Frontend:** https://wonderful-desert-05af0470f.7.azurestaticapps.net
- **Frontend repo:** https://github.com/nagarisn/CloudFinalProject_Frontend

## Stack
- FastAPI + Uvicorn / Gunicorn (Python 3.x)
- SQLAlchemy + pyodbc → Azure SQL Database
- scikit-learn, pandas, numpy for ML
- Deployed via GitHub Actions → Azure App Service

## Endpoints

### Data
| Method | Path | Purpose |
|--------|------|---------|
| GET | `/` | Health check |
| GET | `/household/{hshd_num}` | Joined transactions + households + products, sorted per spec |
| GET | `/dashboard/{hshd_num}` | Aggregate spend / basket / unit metrics |
| GET | `/top-products/{hshd_num}` | Top 5 commodities by spend |
| GET | `/basket-analysis` | Top commodities by purchase count (SQL) |
| GET | `/churn-summary` | Rule-based churn risk buckets |
| POST | `/upload-data` | Upload latest CSV (households / transactions / products) |

### Machine Learning
| Method | Path | Model |
|--------|------|-------|
| GET | `/ml/clv` | Linear Regression (+ Random Forest comparison) — Customer Lifetime Value |
| GET | `/ml/basket` | Association Rule Mining (support / confidence / lift) — cross-sell pairs |
| GET | `/ml/churn` | Gradient Boosting (+ Logistic Regression baseline) — churn probability |

## Local Run
```bash
pip install -r requirements.txt
uvicorn main:app --reload
# docs at http://localhost:8000/docs
```
Set Azure SQL credentials in environment (see `db.py`).

## Files
- `main.py` — FastAPI app, all routes
- `db.py` — SQLAlchemy engine / Azure SQL connection
- `ml_models.py` — CLV, basket association, churn prediction
- `ML_WRITEUP.md` — Required ML model write-up (Req #1)
- `requirements.txt`, `runtime.txt` — Azure App Service config
