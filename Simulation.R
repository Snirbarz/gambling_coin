nflips = 10
n_trials = 10000
M = rep(NA,n_trials)
SD = rep(NA,n_trials)
for (i in 1:n_trials){
  side = sample(c(rep(0,nflips/2),rep(1,nflips/2)),size = nflips)
  outcome = side* rnorm(n = nflips,mean = -10,sd = 3)
  M[i] = mean(outcome)
  SD[i] = sd(outcome)
}
hist(M)
hist(SD)
