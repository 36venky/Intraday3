import numpy as np
import pandas as pd

x = np.array([112451, 114525, 105424])
y = pd.Series(x)

print(y.rank())
