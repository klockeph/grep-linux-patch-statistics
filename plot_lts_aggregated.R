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
library(reshape2)
library(grid)
# library(tikzDevice)

copyrightNotice <- "Philipp Klocke, August 2018, licensed under CC-BY-4.0"

args = commandArgs(trailingOnly=TRUE)

if (length(args) < 1) {
	stop("Usage: plot_aggregated_zero.R LTS_aggregated.csv", call.=FALSE)
}

df <- read.csv(args[[1]])

# fix ordering of kernel versions
df$version <- factor(df$version, levels=unique(df$version))

dfm <- melt(df, id.vars="version")

# tikz(file = "backports.tex", width = 6, height = 3)
X11()

p <- ggplot(data=dfm) +
	geom_col(aes(x=version, y=value, fill=variable)) +
	xlab("Version") +
	ylab("Patches") +
	labs(fill="Tool") +
	ggtitle("Backports") +
	theme_minimal() +
	theme(axis.text.x=element_text(angle=90, hjust=1)) +                            # rotate x labels
	annotation_custom(grobTree(textGrob(copyrightNotice, x=0.01, y=0.95, hjust=0))) # copyright

ggsave("LTS_aggregated.png", plot=p, width=50, height=20, units="cm")

print(p)
# dev.off()

