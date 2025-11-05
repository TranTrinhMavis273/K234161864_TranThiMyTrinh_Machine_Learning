import traceback
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMessageBox
from Connectors.Connector import Connector
from UI.DatabaseConnect import Ui_MainWindow


class DatabaseConnectEx(Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.connector = None
        self.parent = None

    def setupUi(self, MainWindow):
        super().setupUi(MainWindow)
        self.MainWindow = MainWindow

        # gắn sự kiện
        self.pushButtonConnect.clicked.connect(self.safeConnectDatabase)
        self.pushButtonClose.clicked.connect(self.closeWindow)

    # ================================================================
    #  PHIÊN BẢN KẾT NỐI AN TOÀN - KHÔNG BAO GIỜ LÀM APP TẮT
    # ================================================================
    def safeConnectDatabase(self):
        try:
            self.connectDatabase()
        except Exception as e:
            # Chặn MỌI lỗi — kể cả lỗi không mong muốn
            print("=== LỖI NGOÀI DỰ KIẾN ===")
            traceback.print_exc()
            msg = QMessageBox(self.MainWindow)
            msg.setWindowTitle("Unexpected Error")
            msg.setText(f"❌ Lỗi ngoài dự kiến:\n{str(e)}")
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.exec()

    def connectDatabase(self):
        try:
            server = self.lineEditServer.text().strip()
            port = int(self.lineEditPort.text().strip())
            user = self.lineEditUser.text().strip()
            password = self.lineEditPassword.text().strip()
            database = self.lineEditDatabase.text().strip()

            # Ghi log ra console để kiểm tra
            print(f"[INFO] Đang kết nối tới {server}:{port}, DB={database}, user={user}")

            # ======= GỌI CONNECTOR =======
            self.connector = Connector()
            self.connector.server = server
            self.connector.port = port
            self.connector.database = database
            self.connector.username = user
            self.connector.password = password

            # HÀM connect() của Connector cần bọc lỗi bên trong
            try:
                self.connector.connect()
            except Exception as conn_err:
                print("❌ Lỗi khi gọi Connector.connect():", conn_err)
                traceback.print_exc()
                self.connector = None
                QMessageBox.critical(
                    self.MainWindow,
                    "Database Error",
                    f"Không thể kết nối đến MySQL:\n{str(conn_err)}"
                )
                return  # dừng tại đây

            # ======= Nếu thành công =======
            QMessageBox.information(self.MainWindow, "Success", "✅ Kết nối MySQL thành công!")
            self.MainWindow.close()

            if self.parent:
                self.parent.checkEnableWidget(True)

        except ValueError:
            QMessageBox.warning(self.MainWindow, "Input Error", "⚠️ Port phải là số nguyên!")
        except Exception as e:
            print("❌ Lỗi khi tạo Connector:", e)
            traceback.print_exc()
            self.connector = None
            QMessageBox.critical(
                self.MainWindow,
                "Error",
                f"Không thể khởi tạo kết nối:\n{str(e)}"
            )

    def closeWindow(self):
        self.MainWindow.close()

    def show(self):
        self.MainWindow.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.MainWindow.show()
