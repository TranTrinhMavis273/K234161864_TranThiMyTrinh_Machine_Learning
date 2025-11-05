from tkinter import *
from tkinter import ttk
import pandas as pd

class DataSetViewer:
    def __init__(self):
        pass

    def create_ui(self):
        self.root = Tk()
        self.root.title("Data Set Viewer - House Pricing Prediction")
        self.root.geometry("800x600")

        main_panel = PanedWindow(self.root)
        main_panel["bg"] = "lightblue"
        main_panel.pack(fill=BOTH, expand=True)

        columns = (
            'Avg. Area Income',
            'Avg. Area House Age',
            'Avg. Area Number of Rooms',
            'Avg. Area Number of Bedrooms',
            'Area Population',
            'Price' 
        )
        self.tree = ttk.Treeview(main_panel, columns=columns, show='headings')

        self.tree.heading('Avg. Area Income', text='Avg. Area Income')
        self.tree.heading('Avg. Area House Age', text='Avg. Area House Age')
        self.tree.heading('Avg. Area Number of Rooms', text='Avg. Area Number of Rooms')
        self.tree.heading('Avg. Area Number of Bedrooms', text='Avg. Area Number of Bedrooms')
        self.tree.heading('Area Population', text='Area Population')
        self.tree.heading('Price', text='Price')

        self.tree.pack(side=LEFT, fill=BOTH, expand=True)

        scrollbar = ttk.Scrollbar(main_panel, orient=VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)  # <-- đúng thuộc tính là yscrollcommand
        scrollbar.pack(side=RIGHT, fill=Y)

    def show_ui(self):
        self.root.mainloop()

    def show_data_listview(self, fileName):
        df = pd.read_csv(fileName)
        for i in range(len(df)):
            value = [
                df.iloc[i][0],
                df.iloc[i][1],
                df.iloc[i][2],
                df.iloc[i][3],
                df.iloc[i][4],
                df.iloc[i][5],
            ]
            self.tree.insert("", "end", values=value)
