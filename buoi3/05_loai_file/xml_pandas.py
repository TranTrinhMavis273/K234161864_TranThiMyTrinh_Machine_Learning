import pandas_read_xml as pdx
df=pdx.read_xml(r"E:\Machine_learning\hoc_tren_lop\buoi3\SalesTransactions.xml",['UelSample','SaleItem'])
print(df)
print(df.iloc[0])
data=df.iloc[0]
print(data[0])
print(data[1])
print(data[1]["OrderID"])