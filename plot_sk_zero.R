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
library(grid)
library(plyr)

copyrightNotice <- "Philipp Klocke, August 2018, licensed under CC-BY-4.0"

args = commandArgs(trailingOnly=TRUE)

if (length(args) < 1) {
	stop("Usage: plot_sk_zero.R data1.csv [data2.csv]...", call.=FALSE)
}

# read each data file in order
df <- read.csv(args[[1]])
df <- mutate(df, timestamp=as.POSIXct(timestamp, origin="1970-01-01"), version=as.character(version))

# fix ordering of kernel versions
df$version <- factor(df$version, levels=unique(df$version))

p <-ggplot(data=df, aes(x=version, y=syzkaller_patches)) +
	geom_bar(stat="identity", fill="blue") +
	xlab("Versions") +
	ylab("Syzkaller Patches") +
	theme(axis.text.x=element_text(angle=90, hjust=1)) +                                      # rotate x labels
	annotation_custom(grobTree(textGrob(copyrightNotice, x=0.01, y=0.95, hjust=0)))           # copyright


ggsave("syzkaller_patches_zero.png", plot=p, width=50, height=20, units="cm")

