import pandas as pd

nobel = pd.read_csv("nobel-prize-laureates.csv")
nobel = nobel[["awardYear", "category", "name"]]
nobel.to_csv("nobel-prize-laureates.csv")