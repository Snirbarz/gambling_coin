library(dplyr)
df = read.csv("2024-01-03_1011_gambling_task.csv")
df_gamble = df %>% filter(gamble_trial == "yes" & side_1_stim!=8)
sample(df_gamble$loss,1)



