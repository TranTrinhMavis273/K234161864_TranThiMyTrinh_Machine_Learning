from bs4 import BeautifulSoup
with open (r"E:\Machine_learning\hoc_tren_lop\buoi3\SalesTransactions.xml","r") as f:
    data=f.read()
bs_data=BeautifulSoup(data,'xml')
UelSample=bs_data.find_all('UelSample')
print(UelSample)
