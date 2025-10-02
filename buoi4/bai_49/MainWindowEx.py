import base64
import traceback
import mysql.connector
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QMainWindow, QTableWidgetItem, QFileDialog, QMessageBox
)
from MainWindow import Ui_MainWindow


class MainWindowEx(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # default values
        self.default_avatar = "img/ic_no_avatar.png"
        self.id = None
        self.code = None
        self.name = None
        self.age = None
        self.avatar = None
        self.intro = None

        # gắn sự kiện cho các nút
        self.tableWidgetStudent.itemSelectionChanged.connect(self.processItemSelection)
        self.pushButtonAvatar.clicked.connect(self.pickAvatar)
        self.pushButtonremoveAvatar.clicked.connect(self.removeAvatar)
        self.pushButtonInsert.clicked.connect(self.processInsert)
        self.pushButtonUpdate.clicked.connect(self.processUpdate)
        self.pushButtonRemove.clicked.connect(self.processRemove)

        # kết nối MySQL khi khởi tạo
        self.connectMySQL()
        self.selectAllStudent()

    def connectMySQL(self):
        try:
            self.conn = mysql.connector.connect(
                host="localhost",
                port=3306,
                database="studentmanagement",
                user="root",
                password="PkHbr@2f3oOtRH9O4!Cu"
            )
            print("✅ MySQL connected!")
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Database Error", f"Lỗi kết nối: {err}")

    def selectAllStudent(self):
        if self.conn is None:
            QMessageBox.critical(self, "Database Error", "Không có kết nối cơ sở dữ liệu.")
            return
        cursor = self.conn.cursor()
        sql = "SELECT * FROM student"
        cursor.execute(sql)
        dataset = cursor.fetchall()

        self.tableWidgetStudent.setRowCount(0)
        for item in dataset:
            row = self.tableWidgetStudent.rowCount()
            self.tableWidgetStudent.insertRow(row)

            self.tableWidgetStudent.setItem(row, 0, QTableWidgetItem(str(item[0])))
            self.tableWidgetStudent.setItem(row, 1, QTableWidgetItem(item[1]))
            self.tableWidgetStudent.setItem(row, 2, QTableWidgetItem(item[2]))
            self.tableWidgetStudent.setItem(row, 3, QTableWidgetItem(str(item[3])))

        cursor.close()

    def processItemSelection(self):
        row = self.tableWidgetStudent.currentRow()
        if row == -1:
            return
        try:
            code = self.tableWidgetStudent.item(row, 1).text()
            cursor = self.conn.cursor()
            sql = "SELECT * FROM student WHERE Code=%s"
            cursor.execute(sql, (code,))
            item = cursor.fetchone()
            if item:
                self.id, self.code, self.name, self.age, self.avatar, self.intro = item
                self.lineEditId.setText(str(self.id))
                self.lineEditCode.setText(self.code)
                self.lineEditName.setText(self.name)
                self.lineEditAge.setText(str(self.age))
                self.lineEditIntro.setText(self.intro)

                if self.avatar:
                    imgdata = base64.b64decode(self.avatar)
                    pixmap = QPixmap()
                    pixmap.loadFromData(imgdata)
                    self.labelAvatar.setPixmap(pixmap)
                else:
                    self.labelAvatar.setPixmap(QPixmap(self.default_avatar))
            cursor.close()
        except:
            traceback.print_exc()

    def pickAvatar(self):
        filters = "Picture PNG (*.png);;All files(*)"
        filename, _ = QFileDialog.getOpenFileName(self, filter=filters)
        if not filename:
            return
        pixmap = QPixmap(filename)
        self.labelAvatar.setPixmap(pixmap)
        with open(filename, "rb") as f:
            self.avatar = base64.b64encode(f.read())

    def removeAvatar(self):
        self.avatar = None
        self.labelAvatar.setPixmap(QPixmap(self.default_avatar))

    def processInsert(self):
        try:
            cursor = self.conn.cursor()
            sql = "INSERT INTO student (Code,Name,Age,Avatar,Intro) VALUES (%s,%s,%s,%s,%s)"
            self.code = self.lineEditCode.text()
            self.name = self.lineEditName.text()
            age_text = self.lineEditAge.text()
            if not age_text.isdigit():
                QMessageBox.warning(self, "Invalid Input", "Age must be a number.")
                cursor.close()
                return
            self.age = int(age_text)
            self.intro = self.lineEditIntro.text()
            val = (self.code, self.name, self.age, self.avatar, self.intro)
            cursor.execute(sql, val)
            self.conn.commit()
            self.lineEditId.setText(str(cursor.lastrowid))
            cursor.close()
            self.selectAllStudent()
        except:
            traceback.print_exc()

    def processUpdate(self):
        try:
            cursor = self.conn.cursor()
            sql = "UPDATE student SET Code=%s, Name=%s, Age=%s, Avatar=%s, Intro=%s WHERE Id=%s"
            self.id = int(self.lineEditId.text())
            self.code = self.lineEditCode.text()
            self.name = self.lineEditName.text()
            self.age = int(self.lineEditAge.text())
            self.intro = self.lineEditIntro.text()
            val = (self.code, self.name, self.age, self.avatar, self.intro, self.id)
            cursor.execute(sql, val)
            self.conn.commit()
            cursor.close()
            self.selectAllStudent()
        except:
            traceback.print_exc()

    def processRemove(self):
        dlg = QMessageBox(self)
        dlg.setWindowTitle("Confirmation Deleting")
        dlg.setText("Are you sure you want to delete?")
        dlg.setIcon(QMessageBox.Icon.Question)
        buttons = QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        dlg.setStandardButtons(buttons)
        button = dlg.exec()
        if button == QMessageBox.StandardButton.No:
            return
        cursor = self.conn.cursor()
        sql = "DELETE FROM student WHERE Id=%s"
        cursor.execute(sql, (self.lineEditId.text(),))
        self.conn.commit()
        cursor.close()
        self.selectAllStudent()
        self.clearData()

    def clearData(self):
        self.lineEditId.clear()
        self.lineEditCode.clear()
        self.lineEditName.clear()
        self.lineEditAge.clear()
        self.lineEditIntro.clear()
        self.avatar = None
        self.labelAvatar.setPixmap(QPixmap(self.default_avatar))
