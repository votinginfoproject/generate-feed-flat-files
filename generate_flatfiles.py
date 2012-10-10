#!/usr/bin/env python
# -- coding: utf-8 --

import sqlite3
from hashlib import md5
import filetype as ft
import directorytools as dt
import unpack
import feedtoflatfiles as ftff
from os import listdir
from shutil import make_archive, move, rmtree

FEED_DIR = ""
DB_LOC = ""
TEMP_DIR = "temp/"

def setup_db(conn):
	cur = conn.cursor()
	cur.execute("CREATE TABLE IF NOT EXISTS file_data (file_name TEXT, hash TEXT)")

def has_changed(conn, fname):
	cur = conn.cursor()
	cur.execute("SELECT hash FROM file_data WHERE file_name = '" + fname + "'")
	new_hash = file_hash(fname)
	old_vals = cur.fetchone()
	if not old_vals: 
		cur.execute("INSERT INTO file_data (file_name, hash) VALUES('" + fname + "','" + new_hash + "')")
		conn.commit()
		return True
	elif old_vals[0] != new_hash: 
		cur.execute("UPDATE file_data SET hash = '" + new_hash + "' WHERE file_name = '" + fname + "'")
		conn.commit()
		return True
	return False

def file_hash(fname):
	m = md5()
	with open(fname, "rb") as fh:
		for data in fh.read(8192):
			m.update(data)
	return m.hexdigest()

conn = sqlite3.connect(DB_LOC)
setup_db(conn)

folders = listdir(FEED_DIR)
for f in folders:
	files = listdir(FEED_DIR + f)
	for fname in files:
		if fname.startswith("vipFeed") and fname.split(".")[0].endswith("2012-11-06"):
			fullpath = FEED_DIR + f + "/" + fname
			if has_changed(conn, fullpath):
				flatfiledir = fname.split(".")[0] + "_flatfiles/"
				dt.clear_or_create(flatfiledir)
				dt.clear_or_create(TEMP_DIR)
				unpack.unpack(fullpath, TEMP_DIR)
				unpack.flatten_folder(TEMP_DIR)
				xml_file = dt.file_by_extension(".xml", TEMP_DIR)
				ftff.feed_to_db_files(flatfiledir, xml_file)
				make_archive(fname.split(".")[0] + "_flatfiles", "zip", flatfiledir)
				move(fname.split(".")[0] + "_flatfiles.zip", FEED_DIR + f + "/" + fname.split(".")[0] + "_flatfiles.zip")
				rmtree(TEMP_DIR)
				rmtree(flatfiledir)
				
