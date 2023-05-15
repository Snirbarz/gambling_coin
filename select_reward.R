library(dplyr)
df = read.csv("2023-05-10_1008_gambling_task.csv")
df_gamble = df %>% filter(gamble_trial == "yes" & side_1_stim!=8)
sample(df_gamble$loss,1)



