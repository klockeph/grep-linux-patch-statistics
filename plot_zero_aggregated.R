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
# library(tikzDevice)

copyrightNotice <- "Philipp Klocke, BMW AG, December 2018, licensed under CC-BY-4.0"

args = commandArgs(trailingOnly=TRUE)

if (length(args) < 1) {
	stop("Usage: plot_aggregated_zero.R tool1_zero.csv [tool2_zero.csv]...", call.=FALSE)
}

# tikz(file = "aggregated_zero.tex", width = 6, height = 3)
X11()

p <- ggplot() +
	xlab("Version") +
	ylab("Patches") +
	labs(color="Tool") +
	ggtitle("Releases") +
	theme_minimal() +
	theme(axis.text.x=element_text(angle=90, hjust=1))                              # rotate x labels
	annotation_custom(grobTree(textGrob(copyrightNotice, x=0.01, y=0.95, hjust=0))) # copyright

for (arg in args) {
	# read each data file in order
	df <- read.csv(arg)
	df <- mutate(df, timestamp=as.POSIXct(timestamp, origin="1970-01-01"), version=as.character(version))

	df$tool <- strsplit(arg, "_")[[1]][1]
	# fix ordering of kernel versions
	df$version <- factor(df$version, levels=unique(df$version))

	p <- p + geom_point(data=df, aes(x=version, y=patches, group=tool, color=tool)) +
		geom_line(data=df, aes(x=version, y=patches, group=tool, color=tool))
}

ggsave("zero_aggregated.png", plot=p, width=50, height=20, units="cm")

print(p)

