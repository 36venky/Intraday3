import pandas as pd

# Read file (no header)
df = pd.read_csv("1Count.txt", header=None)

# Filter rows where last column > 5
filtered = df[df.iloc[:, -1] > 5]

print(filtered)
