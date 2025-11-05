# Thu vien
import os
from datetime import datetime
from tkinter import *
from tkinter import ttk, messagebox
from tkinter.font import Font
from tkinter import filedialog as fd
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn import metrics

from DataSetViewer import DataSetViewer
from FileUtil import FileUtil

class UIPrediction:
    fileName: str = ""

    def __init__(self):
        pass

    def create_ui(self):
        self.root = Tk()
        self.root.title("House Pricing Prediction- Faculty of Information Systems")
        self.root.geometry("1500x850")

        main_panel = PanedWindow(self.root)
        main_panel["bg"] = "yellow"
        main_panel.pack(fill=BOTH, expand=True)

        top_panel = PanedWindow(main_panel, height=80)
        top_panel["bg"] = "blue"
        main_panel.add(top_panel)
        top_panel.pack(fill=X, side=TOP, expand=False)

        font = Font(family="tahoma", size=18)
        title_label = Label(top_panel, text='House Pricing Prediction', font=font)
        title_label["bg"] = "yellow"
        top_panel.add(title_label)

        center_panel = PanedWindow(main_panel)
        main_panel.add(center_panel)
        center_panel["bg"] = "pink"
        center_panel.pack(fill=BOTH, expand=True)

        # ----------------- Chọn dataset -----------------
        choose_dataset_panel = PanedWindow(center_panel, height=30)
        center_panel.add(choose_dataset_panel)
        choose_dataset_panel["bg"] = "orange"
        choose_dataset_panel.pack(fill=X)

        dataset_label = Label(choose_dataset_panel, text="Select Dataset:")
        self.selectedFileName = StringVar()
        self.selectedFileName.set("dataset/USA_Housing.csv")
        self.choose_dataset_entry = Entry(choose_dataset_panel, textvariable=self.selectedFileName, width=60)
        self.choose_dataset_button = Button(
            choose_dataset_panel, text="1.Pick Dataset", width=15, command=self.do_pick_data
        )
        self.view_dataset_button = Button(
            choose_dataset_panel, text="2.View Dataset", width=15, command=self.do_view_dataset
        )

        choose_dataset_panel.add(dataset_label)
        choose_dataset_panel.add(self.choose_dataset_entry)
        choose_dataset_panel.add(self.choose_dataset_button)
        choose_dataset_panel.add(self.view_dataset_button)

        # ----------------- Training rate + nút train/eval -----------------
        training_rate_panel = PanedWindow(center_panel, height=30)
        center_panel.add(training_rate_panel)
        training_rate_panel.pack(fill=X)

        training_rate_label = Label(training_rate_panel, text="Training Rate:")
        self.training_rate = IntVar()
        self.training_rate.set(80)
        self.training_rate_entry = Entry(training_rate_panel, textvariable=self.training_rate, width=10)

        percent_label = Label(training_rate_panel, text="%", width=5, anchor="w", justify=LEFT)

        training_rate_panel.add(training_rate_label)
        training_rate_panel.add(self.training_rate_entry)
        training_rate_panel.add(percent_label)

        self.train_model_button = Button(
            training_rate_panel, text="3.Train Model", width=20, command=self.do_train
        )
        training_rate_panel.add(self.train_model_button)

        self.evaluate_model_button = Button(
            training_rate_panel, text="4.Evaluate Model", width=20, command=self.do_evaluation
        )
        training_rate_panel.add(self.evaluate_model_button)

        self.status = StringVar()
        self.train_model_result_label = Label(
            training_rate_panel, text=self.status.get(), textvariable=self.status
        )
        training_rate_panel.add(self.train_model_result_label)

        # ----------------- Bảng đánh giá + hệ số -----------------
        evaluate_panel = PanedWindow(center_panel, height=400)
        evaluate_panel["bg"] = "cyan"
        center_panel.add(evaluate_panel)
        evaluate_panel.pack(fill=X)

        table_evaluate_panel = PanedWindow(evaluate_panel, height=400)
        evaluate_panel.add(table_evaluate_panel)

        columns = (
            'Avg. Area Income',
            'Avg. Area House Age',
            'Avg. Area Number of Rooms',
            'Avg. Area Number of Bedrooms',
            'Area Population',
            'Original Price',
            'Prediction Price'
        )
        self.tree = ttk.Treeview(table_evaluate_panel, columns=columns, show="headings")

        self.tree.column("# 1", anchor=CENTER, stretch=NO, width=150)
        self.tree.column("# 2", anchor=CENTER, stretch=NO, width=150)
        self.tree.column("# 3", anchor=CENTER, stretch=NO, width=170)
        self.tree.column("# 4", anchor=CENTER, stretch=NO, width=190)
        self.tree.column("# 5", anchor=CENTER, stretch=NO, width=140)
        self.tree.column("# 6", anchor=CENTER, stretch=NO, width=130)
        self.tree.column("# 7", anchor=CENTER, stretch=NO, width=130)

        self.tree.heading("Avg. Area Income", text="Avg. Area Income")
        self.tree.heading("Avg. Area House Age", text="Avg. Area House Age")
        self.tree.heading("Avg. Area Number of Rooms", text="Avg. Area Number of Rooms")
        self.tree.heading("Avg. Area Number of Bedrooms", text="Avg. Area Number of Bedrooms")
        self.tree.heading("Area Population", text="Area Population")
        self.tree.heading("Original Price", text="Original Price")
        self.tree.heading("Prediction Price", text="Prediction Price")

        self.tree.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar = ttk.Scrollbar(table_evaluate_panel, orient=VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=RIGHT, fill=Y)

        coefficient_panel = PanedWindow(evaluate_panel)
        coefficient_panel["bg"] = "pink"
        coefficient_panel.pack(side=RIGHT, fill=X, expand=False)
        evaluate_panel.add(coefficient_panel)

        coefficient_detail_label = Label(coefficient_panel, text="Coefficient:")
        coefficient_detail_label.pack(side=TOP, fill=X, expand=False)

        coefficient_detail_panel = PanedWindow(coefficient_panel)
        coefficient_detail_panel.pack(side=TOP, expand=False, fill=X)

        self.coefficient_detail_text = Text(coefficient_detail_panel, height=12, width=50)
        scroll = Scrollbar(coefficient_detail_panel)
        self.coefficient_detail_text.configure(yscrollcommand=scroll.set)
        self.coefficient_detail_text.pack(side=LEFT, expand=False, fill=X)
        scroll.config(command=self.coefficient_detail_text.yview)
        scroll.pack(side=RIGHT, fill=Y, expand=True)

        # ----------------- Metrics + Save/Load -----------------
        metric_panel = PanedWindow(coefficient_panel, height=30)
        metric_panel.pack(side=TOP, fill=BOTH, expand=True)

        self.mae_value = DoubleVar()
        mae_label = Label(metric_panel, text="Mean Absolute Error(MAE):")
        mae_label.grid(row=0, column=0, sticky="w")
        mae_entry = Entry(metric_panel, width=20, textvariable=self.mae_value)
        mae_entry.grid(row=0, column=1, sticky="w")

        self.mse_value = DoubleVar()
        mse_label = Label(metric_panel, text="Mean Square Error(MSE):")
        mse_label.grid(row=1, column=0, sticky="w")
        mse_entry = Entry(metric_panel, width=20, textvariable=self.mse_value)
        mse_entry.grid(row=1, column=1, sticky="w")

        self.rmse_value = DoubleVar()
        rmse_label = Label(metric_panel, text="Root Mean Square Error(RMSE):")
        rmse_label.grid(row=2, column=0, sticky="w")
        rmse_entry = Entry(metric_panel, width=20, textvariable=self.rmse_value)
        rmse_entry.grid(row=2, column=1, sticky="w")

# Nút Save Model (có xác nhận)
        savemodel_button = Button(metric_panel, text="5. Save Model", width=20, command=self.do_save_model)
        savemodel_button.grid(row=3, column=1, sticky="w")

        # Panel Load Model + Dropdown list
        loadmodel_panel = PanedWindow(center_panel, height=30)
        loadmodel_panel["bg"] = "yellow"
        loadmodel_panel.pack(fill=X, side=TOP, pady=5)

        loadmodel_button = Button(loadmodel_panel, text="6. Load Model", command=self.do_load_model)
        loadmodel_button.pack(side=LEFT, padx=5)

        # Biến chọn model
        self.model_choice = StringVar()
        self.model_choice.set("")  # giá trị mặc định rỗng
        self.option_menu = OptionMenu(loadmodel_panel, self.model_choice, ())
        self.option_menu.pack(side=LEFT, padx=5)

# Gọi hàm để load danh sách model ban đầu
        self.refresh_model_list()

        # ----------------- Nhập giá trị để dự đoán -----------------
        input_prediction_panel = PanedWindow(center_panel)
        input_prediction_panel.pack(fill=BOTH, side=TOP, expand=True)

        area_income_label = Label(input_prediction_panel, text="Avg. Area Income:")
        area_income_label.grid(row=0, column=0, sticky="e")
        self.area_income_value = DoubleVar()
        area_income_entry = Entry(input_prediction_panel, width=40, textvariable=self.area_income_value)
        area_income_entry.grid(row=0, column=1, sticky="w")

        area_house_age_label = Label(input_prediction_panel, text="Avg. Area House Age:")
        area_house_age_label.grid(row=1, column=0, sticky="e")
        self.area_house_age_value = DoubleVar()
        area_house_age_entry = Entry(input_prediction_panel, width=40, textvariable=self.area_house_age_value)
        area_house_age_entry.grid(row=1, column=1, sticky="w")

        area_number_of_rooms_label = Label(input_prediction_panel, text="Avg. Area Number of Rooms:")
        area_number_of_rooms_label.grid(row=2, column=0, sticky="e")
        self.area_number_of_rooms_value = DoubleVar()
        area_number_of_rooms_entry = Entry(input_prediction_panel, width=40,
                                           textvariable=self.area_number_of_rooms_value)
        area_number_of_rooms_entry.grid(row=2, column=1, sticky="w")

        area_number_of_bedrooms_label = Label(input_prediction_panel, text="Avg. Area Number of Bedrooms:")
        area_number_of_bedrooms_label.grid(row=3, column=0, sticky="e")
        self.area_number_of_bedrooms_value = DoubleVar()
        area_number_of_bedrooms_entry = Entry(input_prediction_panel, width=40,
                                              textvariable=self.area_number_of_bedrooms_value)
        area_number_of_bedrooms_entry.grid(row=3, column=1, sticky="w")

        area_population_label = Label(input_prediction_panel, text="Area Population:")
        area_population_label.grid(row=4, column=0, sticky="e")
        self.area_population_value = DoubleVar()
        area_population_entry = Entry(input_prediction_panel, width=40, textvariable=self.area_population_value)
        area_population_entry.grid(row=4, column=1, sticky="w")

        prediction_button = Button(input_prediction_panel, text="7. Prediction House Pricing",
                                   command=self.do_prediction)
        prediction_button.grid(row=5, column=1, sticky="w")

        prediction_price_label = Label(input_prediction_panel, text="Prediction Price:")
        prediction_price_label.grid(row=6, column=0, sticky="e")

        # <-- thêm biến và Entry hiển thị giá dự đoán
        self.prediction_price_value = DoubleVar()
        prediction_price_entry = Entry(input_prediction_panel, width=40, textvariable=self.prediction_price_value)
        prediction_price_entry.grid(row=6, column=1, sticky="w")

        designedby_panel = PanedWindow(main_panel, height=20)
        designedby_panel["bg"] = "cyan"
        designedby_panel.pack(fill=BOTH, side=BOTTOM)
        designedby_label = Label(designedby_panel, text="Designed by: Tran Duy Thanh")
        designedby_label["bg"] = "cyan"
        designedby_label.pack(side=LEFT)

    def show_ui(self):
        self.root.mainloop()

    def do_pick_data(self):
        filetypes = (("Dataset CSV", "*.csv"), ("All Files", "*.*"))
        s = fd.askopenfilename(title="Choose dataset", initialdir="/", filetypes=filetypes)
        if s:
            self.selectedFileName.set(s)

    def do_view_dataset(self):
        viewer = DataSetViewer()
        viewer.create_ui()
        viewer.show_data_listview(self.selectedFileName.get())
        viewer.show_ui()

    def do_train(self):
        ratio = self.training_rate.get() / 100
        self.df = pd.read_csv(self.selectedFileName.get())

        self.X = self.df[['Avg. Area Income',
                          'Avg. Area House Age',
                          'Avg. Area Number of Rooms',
                          'Avg. Area Number of Bedrooms',
                          'Area Population']]
        self.y = self.df['Price']

        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            self.X, self.y, test_size=1 - ratio, random_state=101
        )

        from sklearn.linear_model import LinearRegression
        self.lm = LinearRegression()
        self.lm.fit(self.X_train, self.y_train)

        self.status.set("Training finished")
        messagebox.showinfo("Info", "Training finished")

    def do_evaluation(self):
        if not hasattr(self, "lm"):
            messagebox.showwarning("Warning", "Please train or load a model first.")
            return

        # Intercept & coefficients
        intercept_value = self.lm.intercept_
        coeff_df = pd.DataFrame(self.lm.coef_, self.X.columns, columns=['Coefficient'])

        # Hiển thị hệ số gọn gàng
        self.coefficient_detail_text.delete("1.0", END)
        self.coefficient_detail_text.insert(END, f"Intercept: {intercept_value}\n")
        self.coefficient_detail_text.insert(END, coeff_df.to_string())

        # Dự đoán và đổ bảng
        predictions = self.lm.predict(self.X_test)
        y_test_array = np.asarray(self.y_test)

        # Xóa bảng cũ nếu có
        for item in self.tree.get_children():
            self.tree.delete(item)

        for i in range(len(self.X_test)):
            values = [
                self.X_test.iloc[i][0],
                self.X_test.iloc[i][1],
                self.X_test.iloc[i][2],
                self.X_test.iloc[i][3],
                self.X_test.iloc[i][4],
                y_test_array[i],
                predictions[i]
            ]
            self.tree.insert('', END, values=values)

        # TÍNH CHỈ SỐ — để ngoài vòng for (fix treo UI)
        mae = metrics.mean_absolute_error(self.y_test, predictions)
        mse = metrics.mean_squared_error(self.y_test, predictions)
        rmse = np.sqrt(mse)

        self.mae_value.set(mae)
        self.mse_value.set(mse)
        self.rmse_value.set(rmse)

        self.status.set("Evaluation finished")
        messagebox.showinfo("Info", "Evaluation finished")

    def do_save_model(self):
        if not hasattr(self, "lm"):
            messagebox.showwarning("Warning", "No model to save. Train or load a model first.")
            return
        ok = FileUtil.savemodel(self.lm, "housingmodel.zip")
        if ok:
            messagebox.showinfo("Info", "Exported model to disk successfully!")
        else:
            messagebox.showerror("Error", "Failed to save model.")

    def do_load_model(self):
        self.lm = FileUtil.loadmodel("housingmodel.zip")
        if self.lm is None:
            messagebox.showerror("Error", "Failed to load model.")
        else:
            self.status.set("Model loaded")
            messagebox.showinfo("Info", "Loading model from disk successfully!")

    def do_prediction(self):
        if not hasattr(self, "lm"):
            messagebox.showwarning("Warning", "Please train or load a model first.")
            return

        try:
            features = [[
                self.area_income_value.get(),
                self.area_house_age_value.get(),
                self.area_number_of_rooms_value.get(),
                self.area_number_of_bedrooms_value.get(),
                self.area_population_value.get()
            ]]
            result = self.lm.predict(features)
            self.prediction_price_value.set(float(result[0]))
        except Exception as e:
            messagebox.showerror("Error", f"Prediction failed: {e}")

    def refresh_model_list(self):
        model_files = [f for f in os.listdir() if f.endswith(".zip")]
        if not model_files:
            model_files = ["(no model found)"]

        menu = self.option_menu["menu"]
        menu.delete(0, "end")
        for model in model_files:
            menu.add_command(label=model, command=lambda m=model: self.model_choice.set(m))

        # nếu có model thì set mặc định model đầu tiên
        if model_files:
            self.model_choice.set(model_files[0])
    def do_load_model(self):
        selected = self.model_choice.get()
        if not selected or selected == "(no model found)":
            messagebox.showwarning("Warning", "No model selected to load.")
            return

        self.lm = FileUtil.loadmodel(selected)
        if self.lm is None:
            messagebox.showerror("Error", f"Failed to load model file: {selected}")
        else:
            self.status.set(f"Loaded {selected}")
            messagebox.showinfo("Info", f"Model '{selected}' loaded successfully!")
