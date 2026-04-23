from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from db import engine
import os
import shutil

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/")
def home():
    return {"message": "Retail backend is running"}


@app.get("/household/{hshd_num}")
def get_household_data(hshd_num: int):
    query = text("""
        SELECT
            t.HSHD_NUM,
            t.BASKET_NUM,
            t.DATE,
            t.PRODUCT_NUM,
            p.DEPARTMENT,
            p.COMMODITY,
            t.SPEND,
            t.UNITS,
            h.LOYALTY_FLAG,
            h.AGE_RANGE,
            h.MARITAL_STATUS,
            h.INCOME_RANGE,
            h.HOMEOWNER_DESC,
            h.HSHD_COMPOSITION,
            h.HH_SIZE,
            h.CHILDREN
        FROM transactions t
        JOIN households h
            ON t.HSHD_NUM = h.HSHD_NUM
        JOIN products p
            ON t.PRODUCT_NUM = p.PRODUCT_NUM
        WHERE t.HSHD_NUM = :hshd_num
        ORDER BY
            t.HSHD_NUM,
            t.BASKET_NUM,
            t.DATE,
            t.PRODUCT_NUM,
            p.DEPARTMENT,
            p.COMMODITY
    """)

    with engine.connect() as conn:
        result = conn.execute(query, {"hshd_num": hshd_num})
        rows = [dict(row._mapping) for row in result]

    return {"household": hshd_num, "results": rows}


@app.get("/dashboard/{hshd_num}")
def get_dashboard(hshd_num: int):
    query = text("""
        SELECT
            COUNT(*) AS total_items,
            COUNT(DISTINCT t.BASKET_NUM) AS total_baskets,
            SUM(t.SPEND) AS total_spend,
            AVG(t.SPEND) AS avg_spend,
            SUM(t.UNITS) AS total_units
        FROM transactions t
        WHERE t.HSHD_NUM = :hshd_num
    """)

    with engine.connect() as conn:
        result = conn.execute(query, {"hshd_num": hshd_num}).fetchone()

    return {
        "household": hshd_num,
        "total_items": int(result.total_items or 0),
        "total_baskets": int(result.total_baskets or 0),
        "total_spend": float(result.total_spend or 0),
        "avg_spend": float(result.avg_spend or 0),
        "total_units": int(result.total_units or 0),
    }


@app.get("/top-products/{hshd_num}")
def top_products(hshd_num: int):
    query = text("""
        SELECT TOP 5
            p.COMMODITY,
            SUM(t.SPEND) AS total_spend
        FROM transactions t
        JOIN products p
            ON t.PRODUCT_NUM = p.PRODUCT_NUM
        WHERE t.HSHD_NUM = :hshd_num
        GROUP BY p.COMMODITY
        ORDER BY total_spend DESC
    """)

    with engine.connect() as conn:
        result = conn.execute(query, {"hshd_num": hshd_num})
        rows = [dict(row._mapping) for row in result]

    return rows


@app.get("/basket-analysis")
def basket_analysis():
    query = text("""
        SELECT TOP 10
            p.COMMODITY,
            COUNT(*) AS purchase_count,
            SUM(t.SPEND) AS total_spend
        FROM transactions t
        JOIN products p
            ON t.PRODUCT_NUM = p.PRODUCT_NUM
        GROUP BY p.COMMODITY
        ORDER BY purchase_count DESC
    """)

    with engine.connect() as conn:
        result = conn.execute(query)
        rows = [dict(row._mapping) for row in result]

    return rows


@app.get("/churn-summary")
def churn_summary():
    query = text("""
        SELECT TOP 20
            t.HSHD_NUM,
            COUNT(DISTINCT t.BASKET_NUM) AS basket_count,
            SUM(t.SPEND) AS total_spend,
            CASE
                WHEN COUNT(DISTINCT t.BASKET_NUM) < 5 AND SUM(t.SPEND) < 50 THEN 'High Risk'
                WHEN COUNT(DISTINCT t.BASKET_NUM) < 10 THEN 'Medium Risk'
                ELSE 'Low Risk'
            END AS churn_risk
        FROM transactions t
        GROUP BY t.HSHD_NUM
        ORDER BY total_spend ASC
    """)

    with engine.connect() as conn:
        result = conn.execute(query)
        rows = [dict(row._mapping) for row in result]

    return rows


@app.post("/upload-data")
async def upload_data(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"message": f"{file.filename} uploaded successfully"}