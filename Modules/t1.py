import pandas as pd

df = pd.read_csv(r"1Valid.txt", header=None)
#print(df[df.iloc[:,-1]>=2])
print(df.iloc[:,-2].mean())