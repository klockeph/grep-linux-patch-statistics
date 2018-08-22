#!/usr/bin/env Rscript

# Copyright 2018 Philipp Klocke, BMW AG
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

library(ggplot2)
library(ggrepel)
library(grid)
library(plyr)

copyrightNotice <- "Philipp Klocke, August 2018, licensed under CC-BY-4.0"

args = commandArgs(trailingOnly=TRUE)

if (length(args) < 1) {
	stop("Usage: plot_sk_lts.R data1.csv [data2.csv]...", call.=FALSE)
}

# returns if the sub-version is divisible by 5
subversion.div5 <- function(x) {
	version <- strsplit(x, '\\.')[[1]]
	if (length(version) < 3) {
		return(TRUE)
	}
	subversion <- strtoi(version[3])
	return(subversion %% 5 == 0)
}

label_if_fifth <- function(x) {
	if (subversion.div5(x))
		return(x)
	return("")
}

# initialize data frame
data <- data.frame(version=character(), timestamp=numeric(), syzkaller_patches=numeric(), lts_version=character())

# read each data file in order
for (filename in args) {
	df <- read.csv(filename)
	df <- mutate(df, timestamp=as.POSIXct(timestamp, origin="1970-01-01"), version=as.character(version))
	# to get the lts version, remove the last part of version
	df$lts_version <- vapply(df$version, function(x) paste(strsplit(x, '\\.')[[1]][0:2], sep='', collapse='.'), "X", USE.NAMES=FALSE)
	# only keep every fifth version
	df$version <- vapply(df$version, label_if_fifth, "X", USE.NAMES=FALSE)
	data <- rbind(data, df)
}

# fix ordering of kernel versions
data$lts_version <- factor(data$lts_version, levels=unique(data$lts_version))

p <-ggplot(data=data, aes(x=timestamp, y=syzkaller_patches, color=lts_version)) +
	geom_point() +
	geom_label_repel(aes(label=version)) +                                                    # labels
	scale_x_datetime(date_breaks='1 month', limits=c(as.POSIXct('2017-06-01'), Sys.time())) + # x ticks
	xlab("Versions") +
	ylab("Syzkaller Patches") +
	theme(axis.text.x=element_text(angle=90, hjust=1)) +                                      # rotate x labels
	annotation_custom(grobTree(textGrob(copyrightNotice, x=0.01, y=0.95, hjust=0)))           # copyright


ggsave("syzkaller_patches_LTS.png", plot=p, width=50, height=20, units="cm")

