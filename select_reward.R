library(dplyr)
df = read.csv("2022-07-19_1001_gambling_task.csv")
df_gamble = df %>% filter(gamble_trial == "yes")
sample(df_gamble$loss,1)

