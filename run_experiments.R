#load required packages, install if needed
packages<-c("caret","Metrics","DAAG","e1071","tree","randomForest","doMC","dummies","kernlab")

load.packages<-function(p) {
  if (!is.element(p, installed.packages()[,1]))
    install.packages(p, dep = TRUE)
  require(p, character.only = TRUE)
}

for( package in packages) {
  load.packages(package)
}

#used if running from RStudio
year <- 2009
#Set to directory data is in
setwd("~/Edifecs/Data/")

#used if running from command line
#args <- commandArgs(trailingOnly = TRUE)
#year <- args[1]
#setwd(args[2])

#load and drop visitlinks
df <- read.csv(paste(year,"_candidates.csv",sep=""))
df$VisitLink<-NULL
df$chronic_conditions<-as.numeric(df$chronic_conditions)

#remove charges with less than 0
df<-df[df$test_charge>0,]

#remove non standard genders
df<-df[df$female>=0,]

#remove outliers
iqr.charge<-IQR(df$test_charge)
quantile.charge<-quantile(df$test_charge)

#remove regular outliers
upper.outliers<-quantile.charge[4]+1.5*iqr.charge
lower.outliers<-quantile.charge[2]-1.5*iqr.charge

#remove extreme outliers only
#upper.outliers<-quantile.charge[4]+3*iqr.charge
#lower.outliers<-quantile.charge[2]-3*iqr.charge

df<-df[df$test_charge <= upper.outliers & df$test_charge >= lower.outliers,]
rm(iqr.charge)
rm(quantile.charge)
rm(upper.outliers)
rm(lower.outliers)

#convert comorbidities, gender, race to factors
for(i in grep('^CM_',names(df))) {
  df[,i]<-as.factor(df[,i])
}
df$female<-as.factor(df$female)
df$race<-as.factor(df$race)

#remove columns with < .1% positive values
bad.cols<-vector()
for( i in 1:ncol(df)){
  if(sum(as.numeric(df[,i])) < (nrow(df)*0.001)){
    bad.cols<-c(bad.cols, i)
  }
}
if(length(bad.cols)>0){
  for(i in length(bad.cols):1){
    df[,bad.cols[i]]<-NULL
  }
}

#remove factors and response variable from dataframe prior to scaling
reserve <- data.frame()
for( i in ncol(df):1) {
  if((is.factor(df[,i]))){ #| (sum(as.numeric(df[,i]) == 0))){
    if(length(reserve)==0){
      reserve<-data.frame(df[,i])
      colnames(reserve)[1]<-colnames(df)[i]
    }
    else{
      reserve[colnames(df)[i]]<-df[,i]
    }
    df[,i]<-NULL
  }
}
response.variable<-df$test_charge
df$test_charge<-NULL

#scale predictors from 0 to 1
df <- data.frame(lapply(df, function(x) scale(x, center = FALSE, scale = max(x,na.rm=TRUE))))

#add reserved variables
df <- cbind(df, reserve)
df$test_charge <- response.variable

rm(reserve)
rm(response.variable)

#remove factor columns with less than 2 levels
bad.cols<-vector()
for( i in 1:ncol(df)){
  if(is.factor(df[,i]) & nlevels(df[,i])<2){
    bad.cols<-c(bad.cols,i)
  }
}
if(length(bad.cols)>0){
  for(i in length(bad.cols):1){
    df[,bad.cols[i]]<-NULL
  }
}

rm(bad.cols)

#create dummy variables
factor.df<-df[,sapply(df,is.factor)]
df<-df[,sapply(df,Negate(is.factor))]
race.matrix<-dummy(factor.df$race)
female.matrix<-dummy(factor.df$female)
factor.df$race<-NULL
factor.df$female<-NULL
data.matrix<-cbind(race.matrix,female.matrix)

for(i in 1:ncol(factor.df)){
  factor.df[,i]<-as.numeric(as.character(factor.df[,i]))
}

for(i in 1:ncol(data.matrix)){
  data.matrix[,i]<-as.numeric(data.matrix[,i])
}

factor.matrix<-as.matrix(factor.df)

data.matrix<-cbind(data.matrix,factor.matrix)

data.matrix.big<-cbind(data.matrix,as.matrix(df))
data.matrix.big<-as.matrix(data.matrix.big)

#Uncomment for M times K fold cross validation
J = 10

#Vectors to contain experiment results
r = vector()
m = vector()
r2 = vector()

data.matrix.big<-data.matrix.big[sample(nrow(data.matrix.big), nrow(data.matrix.big)), ]

#Optional- Take sample of original data.
#sample.proportion<-0.2
#data.matrix.big<-data.matrix.big[sample(nrow(data.matrix.big), sample.proportion*nrow(data.matrix.big)), ]

#Separate predictors and response
response.var<-ncol(data.matrix.big)
x = data.matrix.big[,-response.var]
y = data.matrix.big[,response.var]

for (j in 1:J) {

  message(paste("crossfold: ",j))
  #number of folds
  K = 10
  
  #store values from each fold evaluation
  r2vals = vector()
  ret = data.frame()
  
  samp<-sample(1:nrow(data.matrix.big))
  x.shuffle = x[samp, ]
  y.shuffle = y[samp]
  for(i in 1:K) {
    
    cur<-vector()
    
    #create train and test sets for this fold
    x.train = x.shuffle[which(1:nrow(data.matrix.big)%%K != i%%K), ]
    x.test = x.shuffle[which(1:nrow(data.matrix.big)%%K == i%%K), ]
    
    y.train = y.shuffle[which(1:nrow(data.matrix.big)%%K != i%%K)]
    y.test = y.shuffle[which(1:nrow(data.matrix.big)%%K == i%%K)]
    
    #Select model to test
    model = randomForest(y=y.train, x=x.train,ntree=100)
    #model = svm(y=y.train, x=x.train, kernel="linear", type="eps-regression")
    
    p = predict(model, x.test, type='response')
    
    cur = cbind(y.test, p)
    ret = rbind(ret, cur)
    
  }
  
  #get metrics
  r = c(r,rmse(ret[, 1], ret[, 2]))
  m = c(m,mae(ret[, 1], ret[, 2]))
  r2 = c(r2,cor(ret[, 1], ret[, 2])^2)

}

print(mean(r))
print(mean(m))
print(mean(r2))

print(r)
print(m)
print(r2)
