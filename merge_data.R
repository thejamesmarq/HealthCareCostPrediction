args <- commandArgs(trailingOnly = TRUE)
year<-as.integer(args[1])
path<-args[2]

#year<-2009
#path<-'./Data'

slash<-'/'

if ( .Platform$OS.type == 'windows' ) {
  slash<-'\\'
}

while ( (.Platform$OS.type == 'windows' & substr(path,nchar(path),nchar(path)) == '\\') 
     | (.Platform$OS.type != 'windows' & substr(path,nchar(path),nchar(path)) == '/')) {
  path<-substr(path, 1, nchar(path)-1)
} 

filename.candidates<-paste(path,slash,year,'_candidates.csv',sep="")
filename.comorb<-paste(path,slash,'WA_SID_',year,'_SEVERITY.csv',sep="")
filename.revcds<-paste(path,slash,'WA_SID_',year,'_CHGS.csv',sep="")

data<-merge(read.csv(filename.revcds),merge(read.csv(filename.candidates),read.csv(filename.comorb),by="KEY"),by="KEY")

write.csv(data,paste(path,slash,year,'_candidates.csv',sep=""),row.names=F)
