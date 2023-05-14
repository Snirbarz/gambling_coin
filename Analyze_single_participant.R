#####################################
# Gambling
#####################################
library(dplyr)
df = read.csv("2023-05-03_1005_gambling_task.csv")
df_gamble = df %>% filter(!is.na(sure_option))

library(ggplot2)
ggplot(df_gamble,aes(x = use_imagery,y = loss,color = SD,group = SD))+
 stat_summary(fun = "mean")+facet_wrap(~side_1_stim)+
  coord_cartesian(ylim = c(0,-20))
  
ggplot(df_gamble,aes(x = sure_option,y = response,color = use_imagery,group = use_imagery))+
  stat_summary(fun = "mean",position = 'dodge')+facet_wrap(SD~side_1_stim)

#####################################
# Exposure
#####################################
exp_df = read.csv("2023-05-03_1006_exposure_task.csv")
exp_df = exp_df%>%
  mutate(score = ifelse((match_array==1 & response == 1)|(match_array==0 & response == 0),1,0))
library(ggplot2)
ggplot(exp_df,aes(x = image_stim,score,group = match_array,color = match_array))+
  stat_summary(fun = "mean")
