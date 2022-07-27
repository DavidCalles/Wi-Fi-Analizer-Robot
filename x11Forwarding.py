# import plotly.express as px

# df = px.data.gapminder().query("country=='Canada'")
# fig = px.line(df, x="year", y="lifeExp", title='Life expectancy in Canada')
# fig.show()

import matplotlib.pyplot as plt
fig = plt.plot([1, 2, 3, 4])
plt.ylabel('some numbers')
plt.show()