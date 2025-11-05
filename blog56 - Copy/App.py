from PyQt6.QtWidgets import QMainWindow, QApplication
from UI.MainWindowEx import MainWindowEx

qApp = QApplication([])

# Tạo cửa sổ thật
qmainWindow = QMainWindow()

# Gắn logic & giao diện
window = MainWindowEx()
window.setupUi(qmainWindow)

# Hiển thị cửa sổ
qmainWindow.show()

# Chạy ứng dụng
qApp.exec()