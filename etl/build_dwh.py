import duckdb
import os

def build_data_marts():
    # 1. Настройка путей
    current_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(current_dir)
    raw_data_path = os.path.join(base_dir, 'data', 'raw_data.csv')
    output_dir = os.path.join(base_dir, 'data', 'marts')
    
    if not os.path.exists(raw_data_path):
        print(f"❌ Файл не найден: {raw_data_path}")
        return

    print(f"📦 Загрузка данных из: {raw_data_path}")
    
    with duckdb.connect() as con:
        # 1. Staging (Явно называем 'country' маленькими буквами)
        con.execute(f"""
            CREATE TABLE stg_transactions AS 
            WITH raw_data AS (
                SELECT 
                    InvoiceNo, StockCode, Quantity,
                    strptime(InvoiceDate, '%m/%d/%Y %H:%M') as InvoiceDate,
                    UnitPrice, CustomerID, Country as country
                FROM read_csv_auto('{raw_data_path}', ignore_errors=true)
                WHERE CustomerID IS NOT NULL AND Quantity > 0 AND UnitPrice > 0
                  AND UPPER(StockCode) NOT IN ('POST', 'DOT', 'M', 'D', 'S', 'BANK CHARGES', 'AMZN FEE')
            ),
            user_birthdays AS (
                SELECT CustomerID, MIN(InvoiceDate) as first_seen 
                FROM raw_data GROUP BY 1
            )
            SELECT r.*, 
                   DATE_TRUNC('month', u.first_seen) as cohort_month,
                   DATE_TRUNC('month', r.InvoiceDate) as activity_month,
                   DATE_DIFF('month', CAST(DATE_TRUNC('month', u.first_seen) AS DATE), CAST(DATE_TRUNC('month', r.InvoiceDate) AS DATE)) as month_index
            FROM raw_data r
            JOIN user_birthdays u ON r.CustomerID = u.CustomerID
            WHERE r.InvoiceDate >= u.first_seen;
        """)
        
        # 2. Витрина Retention (country маленькими)
        con.execute("""
            CREATE TABLE dm_cohort_retention AS
            SELECT cohort_month, country, activity_month, month_index,
                   COUNT(DISTINCT CustomerID) as active_users,
                   SUM(Quantity * UnitPrice) as total_revenue
            FROM stg_transactions
            GROUP BY 1, 2, 3, 4
        """)

        # 3. Витрина RFM (country маленькими)
        con.execute("""
            CREATE TABLE dm_rfm_segments AS
            WITH metrics AS (
                SELECT CustomerID, country, MAX(InvoiceDate) as last_p,
                       COUNT(DISTINCT InvoiceNo) as frequency,
                       SUM(Quantity * UnitPrice) as monetary,
                       (SELECT MAX(InvoiceDate) FROM stg_transactions) as mx_d
                FROM stg_transactions GROUP BY 1, 2
            )
            SELECT *,
                   DATE_DIFF('day', CAST(last_p AS DATE), CAST(mx_d AS DATE)) as recency,
                   NTILE(5) OVER (ORDER BY DATE_DIFF('day', CAST(last_p AS DATE), CAST(mx_d AS DATE)) DESC) as r_score,
                   NTILE(5) OVER (ORDER BY frequency ASC) as f_score,
                   NTILE(5) OVER (ORDER BY monetary ASC) as m_score
            FROM metrics;
        """)

        # 4. Сохранение
        os.makedirs(output_dir, exist_ok=True)
        con.execute(f"COPY dm_cohort_retention TO '{os.path.join(output_dir, 'cohort_retention.parquet')}' (FORMAT PARQUET);")
        con.execute(f"COPY dm_rfm_segments TO '{os.path.join(output_dir, 'rfm_segments.parquet')}' (FORMAT PARQUET);")
        
    print(f"🚀 Витрины сохранены.")

if __name__ == "__main__":
    build_data_marts()
