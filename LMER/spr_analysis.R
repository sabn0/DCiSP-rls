# import packages
library(Matrix)
library(lme4)
library(lmerTest)
library(buildmer)
library(jtools)
library(ggplot2)
library(dplyr)
library(hash)
library(fuzzyjoin)
library("data.table")

# load args
args = commandArgs(trailingOnly=TRUE)
spr_data_file <- args[1]

# load data
spr_data <- read.csv(spr_data_file)
print("number of rows used:")
nrow(spr_data)
cat("\n", "\n")

# convert reaction times to numeric
spr_data$WordReactionTime <- as.numeric(as.character(spr_data$WordReactionTime))

# take log of reaction times
spr_data$WordReactionTime <- log(spr_data$WordReactionTime)

# make sure random effects are factors
spr_data$SentenceItem <- as.factor(spr_data$SentenceItem)
spr_data$SubjectNumber <- as.factor(spr_data$SubjectNumber)

# encode fixed variables values (move to mean 0 std 1)
# handle Session
session_map <- c("Before", "After")
names(session_map) <- c("Before", "After")
group_map <- c("RC-enriched", "Control")
names(group_map) <- c("RC-enriched", "Control")
sentenceType_map <- c("ORC", "SRC")
names(sentenceType_map) <- c("ORC", "SRC")

# encodings
session_map <- c(-0.5, 0.5)
names(session_map) <- c("Before", "After")
levels(spr_data$Session) <- sub("Before", session_map["Before"], levels(spr_data$Session))
levels(spr_data$Session) <- sub("After", session_map["After"], levels(spr_data$Session))

# handle Group
group_map <- c(-0.5, 0.5)
names(group_map) <- c("RC-enriched", "Control")
levels(spr_data$Group) <- sub("RC-enriched", group_map["RC-enriched"], levels(spr_data$Group))
levels(spr_data$Group) <- sub("Control", group_map["Control"], levels(spr_data$Group))
# handle Sentence type
sentenceType_map <- c(-0.5, 0.5)
names(sentenceType_map) <- c("ORC", "SRC")
levels(spr_data$SentenceType) <- sub("ORC", sentenceType_map["ORC"], levels(spr_data$SentenceType))
levels(spr_data$SentenceType) <- sub("SRC", sentenceType_map["SRC"], levels(spr_data$SentenceType))

# choose only columns needed
spr_data <- select(
  spr_data,
  X,
  Session,
  Group,
  SentenceType,
  SubjectNumber,
  SentenceItem,
  WordReactionTime
)

# INITIAL MODEL pre-exposure
print("pre-exposure model (table 4)")
before_data <- subset(spr_data, Session == -0.5)
full <- lmer(WordReactionTime ~ Group * SentenceType + (1|SubjectNumber) + (1|SentenceItem), data=before_data, REML=TRUE)
summary(full)
#anova(full)
cat("\n", "\n")

# MAIN MODEL
print("main model (table 5)")
full <- lmer(WordReactionTime ~ Group * SentenceType * Session + 
               (1|SubjectNumber) + (1|SentenceItem), data=spr_data, REML=TRUE)
summary(full)
#anova(full)
cat("\n", "\n")

# POST HOC MODEL post-exposure
print("post-exposure model (appendix 11)")
after_data <- subset(spr_data, Session == 0.5)
full <- lmer(WordReactionTime ~ Group * SentenceType + (1|SubjectNumber) + (1|SentenceItem), data=after_data, REML=FALSE)
summary(full)
#anova(full)
