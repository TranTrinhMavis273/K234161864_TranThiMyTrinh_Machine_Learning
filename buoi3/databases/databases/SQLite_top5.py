import sqlite3
import pandas as pd
db_path = r"E:\Machine_learning\hoc_tren_lop\buoi3\databases\databases\Chinook_Sqlite.sqlite"
def get_customers_with_min_invoices(db_path, N):
    try:
        sqliteConnection = sqlite3.connect(db_path)
        cursor = sqliteConnection.cursor()
        print("DB Init")
        query = f"""
        SELECT c.CustomerId, c.FirstName, c.LastName, COUNT(i.InvoiceId) AS InvoiceCount
        FROM Customer c
        JOIN Invoice i ON c.CustomerId = i.CustomerId
        GROUP BY c.CustomerId, c.FirstName, c.LastName
        HAVING COUNT(i.InvoiceId) >= {N}
        ORDER BY InvoiceCount DESC;
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        df = pd.DataFrame(rows, columns=["CustomerId", "FirstName", "LastName", "InvoiceCount"])
        return df
    except sqlite3.Error as error:
        print("Error occurred -", error)
        return None
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            print("SQLite Connection closed")

N = int(input("Nhập số lượng Invoice tối thiểu (N): "))

result = get_customers_with_min_invoices(db_path, N)

print(f"\nDanh sách khách hàng có >= {N} hóa đơn:")
print(result)
