library(dplyr)
<<<<<<< HEAD
df = read.csv("2023-05-03_1006_gambling_task.csv")
=======
df = read.csv("2023-04-24_1003_gambling_task.csv")
>>>>>>> origin/main
df_gamble = df %>% filter(gamble_trial == "yes")
sample(df_gamble$loss,1)

