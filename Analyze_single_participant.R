#####################################
# Gambling
#####################################
library(dplyr)
df = read.csv("2022-07-19_1001_gambling_task.csv")
df_gamble = df %>% filter(gamble_trial == "yes" & Block== "test")

library(ggplot2)
ggplot(df_gamble,aes(x = trial,y = loss,color = SD,group = SD))+
 stat_summary(fun = "mean")+facet_wrap(~Mu)
  
ggplot(df_gamble,aes(x = sure_option,y = response,color = SD,group = SD))+
  stat_summary(fun = "mean")+facet_wrap(~Mu)

#####################################
# Exposure
#####################################
exp_df = read.csv("2022-07-19_1001_exposure_task.csv")
exp_df = exp_df%>%
  mutate(score = ifelse((match_array==1 & response == 1)|(match_array==0 & response == 0),1,0))
library(ggplot2)
ggplot(exp_df,aes(x = image_stim,score,group = match_array,color = match_array))+
  stat_summary(fun = "mean")
