library(dplyr)
df = read.csv("2023-05-03_1006_gambling_task.csv")
df_gamble = df %>% filter(gamble_trial == "yes")
sample(df_gamble$loss,1)

