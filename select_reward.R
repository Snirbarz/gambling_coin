library(dplyr)
df = read.csv("2023-04-24_1003_gambling_task.csv")
df_gamble = df %>% filter(gamble_trial == "yes")
sample(df_gamble$loss,1)

