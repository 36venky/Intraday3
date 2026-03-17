from sklearn.linear_model import LinearRegression
import numpy as np
import matplotlib.pyplot as plt

X = np.array([[1],[2],[3],[4],[5]])  # feature (time)
y = np.array([100,105,110,120,130])  # price

model = LinearRegression()
model.fit(X, y)

prediction = model.predict([[6]])
plt.scatter(X, y, color='blue')
plt.plot(X, model.predict(X), color='red')
plt.show()