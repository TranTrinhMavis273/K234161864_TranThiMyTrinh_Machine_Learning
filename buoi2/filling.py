from numpy import nan as NA
import pandas as pd
data =pd.DataFrame([[1., 6.5, 3.],
                    [1., NA, NA],
                    [NA, NA, NA],
                    [NA, 6.5, 3.],
                    [5., 9.5, 3.],
                    [2., 10.1, NA]])
print(data)
print("-"*10)      
cleanded=data.fillna(data.mean())
print(cleanded)