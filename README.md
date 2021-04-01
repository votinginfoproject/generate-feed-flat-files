generate-feed-flat-files
========================

## Installation

You'll want to start the virtual environment you created to run quick_feed:

	$ source ~/envs/qf1/bin/activate

## Usage

	$ cd ~/generate-feed-flat-files/
	$ python feedtoflatfiles.py --d ~/data/[state]/ ~/data/[state]/[XMLfilename.xml].

The resulting flat data files will be in the directory you specified with the option --d.
