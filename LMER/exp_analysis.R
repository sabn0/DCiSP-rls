
# import packages
library(Matrix)
library(lme4)
library(lmerTest)
library(jtools)
library(ggplot2)
library(dplyr)
library(hash)

# load args
args = commandArgs(trailingOnly=TRUE)
exp_data_file <- args[1]

# load data
exp_data <- read.csv(exp_data_file)

# slice reaction times
exp_data <- subset(exp_data, SectionTime == '-')

# choose only columns needed
exp_data <- select(exp_data, X, SubjectNumber, Group, ReadingPassage, QuestionID, Answer)
print("number of rows used:")
nrow(exp_data)
cat("\n", "\n")

# convert answers to numeric
exp_data$Answer <- as.numeric(as.character(exp_data$Answer))

# compute mixed model
print("main model:")
full <- glmer(Answer ~ Group * ReadingPassage + (1|SubjectNumber) + (1|QuestionID), 
             data=exp_data, family="binomial")
summary(full)
#anova(full)

