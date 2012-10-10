import magic
import csv
import xml.sax

TYPE_MAPPING = {"gzip":"gz", "bzip2":"bz2", "Zip":"zip", "RAR":"rar", "POSIX tar":"tar"}
COMPRESSION = ["gz", "bz2"]
ARCHIVED = ["zip", "rar", "tar"]


m = magic.Magic()

def get_type(fname):
    ftype = m.from_file(fname)

    for k in TYPE_MAPPING.keys():
        if k in ftype:
            return TYPE_MAPPING[k]

    #solutions here from http://stackoverflow.com/questions/9084228/python-to-check-if-a-gzipped-file-is-xml-or-csv
    #and http://stackoverflow.com/questions/2984888/check-if-file-has-a-csv-format-with-python
    if 'text' in ftype:

        with open(fname, 'rb') as fh:

            try:
                xml.sax.parse(fh, xml.sax.ContentHandler())
                return 'xml'
            except: # SAX' exceptions are not public
                pass

            fh.seek(0)

            #if line count is less than 2, csv type check will not be accurate
            #so txt is returned as default
            linecount = 0
            for line in fh:
                linecount += 1
                if linecount > 2:
                    break
            if linecount <= 2:
                return 'txt'
                        
            fh.seek(0)
            try:
                dialect = csv.Sniffer().sniff(fh.read(1024))
                return 'csv'
            except csv.Error:
                pass

        return 'txt'

def is_compression(fname):
    ftype = get_type(fname)
    return is_compression_by_type(ftype)

def is_compression_by_type(ftype):
    if ftype in COMPRESSION:
        return True
    return False
	
def is_archived(fname):
    ftype = get_type(fname)
    return is_archived_by_type(ftype)

def is_archived_by_type(ftype):
    if ftype in ARCHIVED:
        return True
    return False
