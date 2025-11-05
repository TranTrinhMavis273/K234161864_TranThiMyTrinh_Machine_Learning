import mysql.connector
from mysql.connector import Error
import traceback
import pandas as pd

class Connector:
    def __init__(self, server=None, port=None, database=None, username=None, password=None):
        self.server = server
        self.port = port
        self.database = database
        self.username = username
        self.password = password
        self.conn = None  # ✅ đảm bảo luôn tồn tại

    def connect(self):
        try:
            print(f"[DEBUG] Connecting to MySQL: host={self.server}, port={self.port}, db={self.database}, user={self.username}")
            self.conn = mysql.connector.connect(
                host=self.server,
                port=self.port,
                database=self.database,
                user=self.username,
                password=self.password
            )

            # ✅ kiểm tra kết nối
            if self.conn.is_connected():
                print("✅ Connected to MySQL successfully!")
                return self.conn
            else:
                print("⚠️ Connection object returned False!")
                raise Exception("Connection object returned False")

        except Error as e:
            print("❌ MySQL connection failed:", e)
            traceback.print_exc()
            # ném lại lỗi để lớp UI xử lý bằng popup
            raise Exception(f"MySQL connection failed: {e}")

        except Exception as e:
            print("❌ Unexpected error:", e)
            traceback.print_exc()
            raise Exception(str(e))

    def disConnect(self):
        if self.conn is not None:
            try:
                self.conn.close()
                print("✅ MySQL connection closed.")
            except:
                traceback.print_exc()

    def queryDataset(self, sql):
        try:
            if self.conn is None:
                raise Exception("Database not connected")
            cursor = self.conn.cursor()
            cursor.execute(sql)
            df = pd.DataFrame(cursor.fetchall())
            if not df.empty:
                df.columns = cursor.column_names
            return df
        except Exception as e:
            print("❌ Query error:", e)
            traceback.print_exc()
            return None

    def getTablesName(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SHOW TABLES;")
            results = cursor.fetchall()
            return [item[0] for item in results]
        except:
            traceback.print_exc()
            return []
