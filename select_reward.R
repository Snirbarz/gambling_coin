library(dplyr)
df = read.csv("2023-03-20_test_gambling_task.csv")
df_gamble = df %>% filter(gamble_trial == "yes")
sample(df_gamble$loss,1)

