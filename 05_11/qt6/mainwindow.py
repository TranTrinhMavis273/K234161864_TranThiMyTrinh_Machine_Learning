import os
import pickle
from datetime import datetime

import numpy as np
import pandas as pd
from PyQt6.QtWidgets import (
    QMainWindow, QFileDialog, QMessageBox, QTableWidgetItem, QApplication
)
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn import metrics

from ui_mainwindow import Ui_MainWindow

DATASET_DEFAULT = "dataset/USA_Housing.csv"
MODEL_DIR = "model"


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        os.makedirs(MODEL_DIR, exist_ok=True)

        self.txtDataset.setText(DATASET_DEFAULT)
        self.btnPick.clicked.connect(self.pick_dataset)
        self.btnView.clicked.connect(self.view_dataset)
        self.btnTrain.clicked.connect(self.train_model)
        self.btnEval.clicked.connect(self.evaluate_model)
        self.btnSave.clicked.connect(self.save_model)
        self.btnLoad.clicked.connect(self.load_model)
        self.btnPredict.clicked.connect(self.predict_once)

        self.lm = None
        self.df = None
        self.X = self.y = None
        self.X_train = self.X_test = self.y_train = self.y_test = None

        self.refresh_model_list()

    # ---------- Dataset ----------
    def pick_dataset(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Choose dataset", "", "CSV Files (*.csv);;All Files (*.*)"
        )
        if path:
            self.txtDataset.setText(path)

    def view_dataset(self):
        try:
            df = pd.read_csv(self.txtDataset.text()).head(100)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Cannot read dataset:\n{e}")
            return
        # Hiển thị sơ bộ trong bảng chính
        self.tblEval.clearContents()
        self.tblEval.setRowCount(df.shape[0])
        self.tblEval.setColumnCount(min(7, df.shape[1]))
        self.tblEval.setHorizontalHeaderLabels(list(df.columns[:7]))
        for r in range(df.shape[0]):
            for c in range(min(7, df.shape[1])):
                self.tblEval.setItem(r, c, QTableWidgetItem(str(df.iat[r, c])))

    # ---------- Train ----------
    def train_model(self):
        try:
            self.df = pd.read_csv(self.txtDataset.text())
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Cannot read dataset:\n{e}")
            return

        try:
            self.X = self.df[['Avg. Area Income', 'Avg. Area House Age',
                              'Avg. Area Number of Rooms', 'Avg. Area Number of Bedrooms',
                              'Area Population']]
            self.y = self.df['Price']
        except KeyError as e:
            QMessageBox.critical(self, "Error",
                                 f"Columns missing: {e}\nCheck your CSV headers.")
            return

        ratio = self.spnRate.value() / 100.0
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            self.X, self.y, test_size=1 - ratio, random_state=101
        )

        self.lm = LinearRegression()
        self.lm.fit(self.X_train, self.y_train)

        self.lblStatus.setText("Training finished.")
        QMessageBox.information(self, "Info", "Training finished.")

    # ---------- Evaluate ----------
    def evaluate_model(self):
        if self.lm is None or self.X_test is None:
            QMessageBox.warning(self, "Warning", "Please train or load a model first.")
            return

        # coefficients
        intercept = self.lm.intercept_
        coeff = pd.DataFrame(self.lm.coef_, self.X.columns, columns=['Coefficient'])
        self.txtCoeff.setPlainText(f"Intercept: {intercept}\n{coeff.to_string()}")

        # predictions
        pred = self.lm.predict(self.X_test)
        yv = self.y_test.to_numpy()
        Xv = self.X_test.values

        self.tblEval.clear()
        headers = [
            'Avg. Area Income', 'Avg. Area House Age', 'Avg. Area Number of Rooms',
            'Avg. Area Number of Bedrooms', 'Area Population', 'Original Price', 'Prediction Price'
        ]
        self.tblEval.setColumnCount(len(headers))
        self.tblEval.setHorizontalHeaderLabels(headers)
        self.tblEval.setRowCount(len(yv))

        for i in range(len(yv)):
            row = list(Xv[i]) + [yv[i], pred[i]]
            for j, v in enumerate(row):
                self.tblEval.setItem(i, j, QTableWidgetItem(str(v)))

        mae = metrics.mean_absolute_error(self.y_test, pred)
        mse = metrics.mean_squared_error(self.y_test, pred)
        rmse = np.sqrt(mse)
        self.txtMAE.setText(f"{mae}")
        self.txtMSE.setText(f"{mse}")
        self.txtRMSE.setText(f"{rmse}")

        self.lblStatus.setText("Evaluation is finished.")
        QMessageBox.information(self, "Info", "Evaluation is finished.")

    # ---------- Save/Load ----------
    def refresh_model_list(self):
        files = [f for f in os.listdir(MODEL_DIR) if f.endswith(".zip")]
        self.cmbModels.clear()
        if files:
            self.cmbModels.addItems(sorted(files))
        else:
            self.cmbModels.addItem("(no model found)")

    def save_model(self):
        if self.lm is None:
            QMessageBox.warning(self, "Warning", "No model to save.")
            return
        confirm = QMessageBox.question(
            self, "Confirm Save", "Do you want to save this trained model?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"housingmodel_{now}.zip"
        path = os.path.join(MODEL_DIR, filename)
        try:
            with open(path, "wb") as f:
                pickle.dump(self.lm, f)
            QMessageBox.information(self, "Saved", f"Saved as:\n{filename}")
            self.refresh_model_list()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Save failed:\n{e}")

    def load_model(self):
        name = self.cmbModels.currentText()
        if not name or name == "(no model found)":
            QMessageBox.warning(self, "Warning", "No model selected.")
            return
        path = os.path.join(MODEL_DIR, name)
        try:
            with open(path, "rb") as f:
                self.lm = pickle.load(f)
            self.lblStatus.setText(f"Loaded {name}")
            QMessageBox.information(self, "Loaded", f"Model '{name}' loaded.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Load failed:\n{e}")

    # ---------- Predict ----------
    def predict_once(self):
        if self.lm is None:
            QMessageBox.warning(self, "Warning", "Please train or load a model first.")
            return
        x = [[
            self.spnIn.value(),
            self.spnAge.value(),
            self.spnRooms.value(),
            self.spnBeds.value(),
            self.spnPop.value()
        ]]
        try:
            pred = self.lm.predict(x)[0]
            self.txtPred.setText(f"{pred}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Prediction failed:\n{e}")
