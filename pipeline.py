"""
RetailMart Pvt. Ltd. — Data Engineering Pipeline
Author  : [Manish Mishra]
Purpose : Load → Clean → Transform → Load to DB → Report
"""

import pandas as pd
import numpy as np
import sqlite3
from sqlalchemy import create_engine
# add after line 10
SALES_FILE    = "sales_data.csv"
PRODUCTS_FILE = "products.csv"
STORES_FILE   = "stores.csv"
DB_PATH       = "sqlite:///retailmart.db"


# TASK 1 — DATA INGESTION


def task1_load_data():
    """Load all three CSV files into pandas DataFrames."""
    df_sales    = pd.read_csv(SALES_FILE)
    df_products = pd.read_csv(PRODUCTS_FILE)
    df_stores   = pd.read_csv(STORES_FILE)

    # Print shape (rows, columns) and first 5 rows of each
    print("\n--- sales_data.csv ---")
    print(f"Shape: {df_sales.shape}")
    print(df_sales.head())

    print("\n--- products.csv ---")
    print(f"Shape: {df_products.shape}")
    print(df_products.head())

    print("\n--- stores.csv ---")
    print(f"Shape: {df_stores.shape}")
    print(df_stores.head())

    # Check for missing values in all DataFrames
    print("\n--- Missing Values Summary ---")
    print("\nsales_data missing values:")
    print(df_sales.isnull().sum())
    # add after line 43
    missing_rows = df_sales[df_sales.isnull().any(axis=1)]
    if not missing_rows.empty:
        print("Rows with missing values:")
        print(missing_rows[["sale_id", "store_id", "product_id", "quantity", "amount"]])
    print("\nproducts missing values:")
    print(df_products.isnull().sum())

    print("\nstores missing values:")
    print(df_stores.isnull().sum())

    return df_sales, df_products, df_stores



# TASK 2 — DATA CLEANING


def task2_clean_data(df_sales):
    """Remove duplicates, fill missing values, fix data types."""
    print("\n" + "=" * 60)
    print("TASK 2: DATA CLEANING")
    print("=" * 60)

    # Step 3: Remove duplicate rows
    before = len(df_sales)
    # line 66 — fixed
    df_sales = df_sales.drop_duplicates(subset=["sale_id"]).reset_index(drop=True)
    after = len(df_sales)
    print(f"\nDuplicates found and removed: {before - after}")

    # Step 4: Fill missing 'quantity' with 0, drop rows where 'amount' is NULL
    df_sales["quantity"] = df_sales["quantity"].fillna(0).astype(int)
    # add after line 71
    zero_qty = df_sales[df_sales["quantity"] == 0]
    if not zero_qty.empty:
        print(f"ℹ {len(zero_qty)} rows had missing quantity (set to 0), removing them:")
        print(zero_qty[["sale_id", "store_id", "product_id"]])
    df_sales = df_sales[df_sales["quantity"] > 0]
    df_sales = df_sales.dropna(subset=["amount"])
    print(f"Cleaned sales_data shape: {df_sales.shape}")

    # Step 5: Convert data types
    df_sales["sale_date"] = pd.to_datetime(df_sales["sale_date"]).dt.strftime("%Y-%m-%d")  # date format
    df_sales["amount"]    = df_sales["amount"].astype(float)         # float type
    print("\nData types after cleaning:")
    print(df_sales.dtypes)

    print("\nCleaned sales_data preview:")
    print(df_sales)

    return df_sales



# TASK 3 — DATA TRANSFORMATION


def task3_transform_data(df_sales, df_products, df_stores):
    """Merge DataFrames, add total_revenue column, group by city."""
    print("\n" + "=" * 60)
    print("TASK 3: DATA TRANSFORMATION")
    print("=" * 60)

    # Step 6: Merge all three DataFrames
    # First merge sales + products on product_id
    df_merged = pd.merge(df_sales, df_products, on="product_id", how="left")
    # Then merge result + stores on store_id
    df_merged = pd.merge(df_merged, df_stores, on="store_id", how="left")

    print("\n--- Final Merged DataFrame ---")
    print(df_merged)

    # Step 7: Add 'total_revenue' column = quantity × price
    df_merged["total_revenue"] = df_merged["quantity"] * df_merged["price"]
    # add after line 107
    mismatch = df_merged[abs(df_merged["amount"] - df_merged["total_revenue"]) > 0.01]
    if not mismatch.empty:
        print(f"⚠ {len(mismatch)} rows have amount ≠ quantity×price:")
        print(mismatch[["sale_id", "product_name", "amount", "total_revenue"]])

    # Use NumPy to calculate stats
    revenue_array = df_merged["total_revenue"].values   # convert to numpy array
    print(f"\ntotal_revenue stats (using NumPy):")
    print(f"  Mean : ₹{np.mean(revenue_array):.2f}")
    print(f"  Max  : ₹{np.max(revenue_array):.2f}")
    print(f"  Min  : ₹{np.min(revenue_array):.2f}")

    # Step 8: Group by city → total revenue per city (descending)
    city_revenue = (
        df_merged.groupby("city")["total_revenue"]
        .sum()
        .reset_index()
        .rename(columns={"total_revenue": "total_city_revenue"})
        .sort_values("total_city_revenue", ascending=False)
    )
    print("\n--- Total Revenue Per City (Sorted Descending) ---")
    print(city_revenue)
    return df_merged



# TASK 4 — DATA LOADING TO SQLite DATABASE


def task4_load_to_db(df_merged):
    """Save final DataFrame to SQLite database."""
    print("\n" + "=" * 60)
    print("TASK 4: DATA LOADING (SQL)")
    print("=" * 60)

    # Step 9: Load into SQLite using sqlalchemy
    engine = create_engine("sqlite:///retailmart.db")
    # add before line 142
    cols = ["sale_id", "sale_date", "store_name", "city", "region",
        "product_name", "category", "quantity", "price", "total_revenue"]
    # line 142 — change to
    df_merged[cols].to_sql("retail_sales", con=engine, if_exists="replace", index=False)
    print("\n✅ Data loaded into SQLite database 'retailmart.db', table 'retail_sales'")

    # Step 10: Top 3 best-selling products by total quantity sold
    query_top3 = """
        SELECT product_name, SUM(quantity) AS total_quantity_sold
        FROM retail_sales
        GROUP BY product_name
        ORDER BY total_quantity_sold DESC
        LIMIT 3;
    """
    top3_products = pd.read_sql_query(query_top3, con=engine)

    print("\n--- Top 3 Best-Selling Products by Quantity ---")
    print(top3_products)

    return engine



# TASK 5 — REPORTING & INSIGHTS


def task5_report(engine):
    """Generate SQL reports and a Python summary."""
    print("\n" + "=" * 60)
    print("TASK 5: REPORTING & INSIGHTS")
    print("=" * 60)

    with sqlite3.connect("retailmart.db") as conn:

        # Step 11: Total revenue per store per day
        query_store_day = """
            SELECT store_name, sale_date, SUM(total_revenue) AS daily_revenue
            FROM retail_sales
            GROUP BY store_name, sale_date
            ORDER BY store_name, sale_date;
        """
        store_day_revenue = pd.read_sql_query(query_store_day, conn)
        print("\n--- Total Revenue Per Store Per Day ---")
        print(store_day_revenue.to_string(index=False))

        # Step 12: Summary Report
        total_transactions = pd.read_sql_query(
            "SELECT COUNT(*) AS total FROM retail_sales", conn
        ).iloc[0, 0]

        total_revenue = pd.read_sql_query(
            "SELECT SUM(total_revenue) AS total FROM retail_sales", conn
        ).iloc[0, 0]

        top_city = pd.read_sql_query(
            """SELECT city, SUM(total_revenue) AS rev
               FROM retail_sales GROUP BY city
               ORDER BY rev DESC LIMIT 1""", conn
        ).iloc[0, 0]

        top_product = pd.read_sql_query(
            """SELECT product_name, SUM(quantity) AS qty
               FROM retail_sales GROUP BY product_name
               ORDER BY qty DESC LIMIT 1""", conn
        ).iloc[0, 0]

    print("\n" + "=" * 60)
    print("         📊 RETAILMART — SUMMARY REPORT")
    print("=" * 60)
    print(f"  Total Transactions  : {total_transactions}")
    print(f"  Total Revenue       : ₹{total_revenue:,.2f}")
    print(f"  Top Selling City    : {top_city}")
    print(f"  Top Selling Product : {top_product}")
    print("=" * 60)



# TASK 6 — FULL PIPELINE WITH ERROR HANDLING


def run_pipeline():
    """
    Master function that runs the full pipeline:
    Load → Clean → Transform → Load to DB → Report
    """
    print("\n🚀 Starting RetailMart Data Pipeline...\n")

    try:
        # Step 1-2: Load data
        df_sales, df_products, df_stores = task1_load_data()
    except FileNotFoundError as e:
        print(f" ERROR: CSV file not found — {e}")
        print("Please make sure sales_data.csv, products.csv, and stores.csv exist.")
        return
    except Exception as e:
        print(f" ERROR while loading data: {e}")
        return

    try:
        # Step 3-5: Clean data
        df_sales_clean = task2_clean_data(df_sales)
    except Exception as e:
        print(f" ERROR during data cleaning: {e}")
        return

    # lines 252–264 — fixed order
    try:
        df_merged = task3_transform_data(df_sales_clean, df_products, df_stores)
    except Exception as e:
        print(f" ERROR during data transformation: {e}")
        return

    try:
        engine = task4_load_to_db(df_merged)
    except Exception as e:
        print(f" ERROR while loading to database: {e}")
        return

    try:
        task5_report(engine)
    except Exception as e:
        print(f" ERROR during reporting: {e}")
        return
    finally:
        engine.dispose()   # ← moved here, runs after reporting is done

    print("\n Pipeline completed successfully ! ")



# Entry point

if __name__ == "__main__":
    run_pipeline()
