import sys
import os
from PyQt6.QtWidgets import QApplication
from mainwindow import MainWindow

if __name__ == "__main__":
    # tạo thư mục dataset/model nếu chưa có
    os.makedirs("dataset", exist_ok=True)
    os.makedirs("model", exist_ok=True)

    app = QApplication(sys.argv)
    w = MainWindow()
    w.resize(1200, 780)
    w.show()
    sys.exit(app.exec())
