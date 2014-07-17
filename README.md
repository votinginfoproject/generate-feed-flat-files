generate-feed-flat-files
========================

## Usage
The simplest way to run this is with Docker.

1. `docker build -t ftff .`
1. `docker run -v /your/data/dir:/data -v /your/feed/output/dir:/feeds ftff /data/vipFeed-xx-yyyy-mm-dd.xml`
