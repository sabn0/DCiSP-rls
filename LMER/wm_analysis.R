
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
wm_data_file <- args[1]

# load data
wm_data <- read.csv(wm_data_file)

# slice on pre-exposure answers
wm_data <- subset(wm_data, Session == 'Start')
print("number of rows used:")
nrow(wm_data)
cat("\n", "\n")

# choose only columns needed
wm_data <- select(wm_data, X, Script, WMResult)

# convert scores to numeric
wm_data$WMResult <- as.numeric(as.character(wm_data$WMResult))

# compute mixed model
full <- aov(WMResult ~ Script, data=wm_data)
summary(full)
