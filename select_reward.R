library(dplyr)
df = read.csv("2022-06-02__gambling_task.csv")
df_gamble = df %>% filter(gamble_trial == "yes")
sample(df_gamble$loss,1)

