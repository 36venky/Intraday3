# import pandas as pd

# # Read file (no header)
# df = pd.read_csv("1Count.txt", header=None)

# # Filter rows where last column > 5
# filtered = df[df.iloc[:, -1] > 5]

# print(filtered)
from collections import defaultdict
import time as t
h = defaultdict(list)

def add_value(key, value):
    h[key].append(value)
    R2 = h[key].copy()
    if len(h[key]) < 3:
        return False, False, 0.0, value,R2

    last3 = h[key][-3:]

    diffs = [
        last3[1] - last3[0],
        last3[2] - last3[1]
    ]

    mean_diff = round(sum(diffs) / len(diffs), 2)
    latest = last3[-1]

    # trend checks
    n1 = last3[1] >= last3[0] and last3[2] >= last3[1]
    n2 = last3[2] >= 0.65
    print(last3[2])
    near = n1 and n2

    if mean_diff >= 0.11 and latest >= 0.70:
        return True, near, mean_diff, latest, R2
    else:
        return False, near, mean_diff, latest, R2
    

l = [57,71,89]
for i in range(3):
    a = l[i]
    print(add_value('SCI',a))
    t.sleep(2)