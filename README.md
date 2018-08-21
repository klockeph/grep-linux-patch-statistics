# syzkaller-patch-statistics
Scripts to show syzkallers impact on recent linux kernel development

# Requirements
- python3
- RScript
	- ggplot2
	- ggrepel
	- grid
	- plyr
- linux-stable git

# Usage
Move `get_syzkaller_patch_data.py` into a linux-stable directory. You can then call this script to generate `syzkaller_zero.csv` and `syzkaller_<LTS_Version>.csv`.
The optional parameter `-f, --filter` allows to specify what to grep for in git logs. It defaults to `syzkaller.appspotmail.com`.

## Dot-Zero Versions
Call `plot_sk_zero.R syzkaller_zero.csv` to generate `syzkaller_patches_zero.png`.
![Syzkaller Zero](syzkaller_patches_zero.png)


## LTS Versions
Call `plot_sk_lts.R syzkaller_<LTS_Version>.csv [syzkaller_<LTS_Version>.csv]...` to generate `syzkaller_patches_LTS.png`. Note that you have to supply the .csv files in correct order.
![Syzkaller LTS](syzkaller_patches_LTS.png)


