generate-feed-flat-files
========================

## Usage
The simplest way to run this is with Docker.

1. `docker build -t ftff .`
1. `docker run -v /your/data/dir:/data -v /your/feed/output/dir:/feeds ftff /data/vipFeed-xx-yyyy-mm-dd.xml`

## Installation

If you're not using Docker (and are on a Mac), you'll want to start the virtual environment you created to run quick_feed: 

	$ source ~/envs/qf1/bin/activate
	$ cd ~/generate-feed-flat-files/
	$ python feedtoflatfiles.py --d ~/data/[state]/ ~/data/[state]/[XMLfilename.xml]. 
	
The resulting flat data files will be in the directory you specified with the option --d.