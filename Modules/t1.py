import pandas as pd

df = pd.read_csv(r"1Invalid.txt", header=None)
print(df[df.iloc[:,2]>0.9].loc[:,0])