from lxml import etree
from csv import DictWriter, DictReader
from os import path
from copy import copy
import csv
from schemaprops import SchemaProps

SCHEMA_URL = "https://github.com/votinginfoproject/vip-specification/raw/master/vip_spec_v3.0.xsd"

def clear_element(element):
	element.clear()
	while element.getprevious() is not None:
		del element.getparent()[0]

def extract_base_elements(context, element_list):
	for event, element in context:
		if event == "end" and element.tag in element_list and len(element.getchildren()) > 0:
			yield element
			clear_element(element)

def file_writer(directory, e_name, fields):

	output_file = directory + e_name + ".txt"
		
	if path.exists(output_file):
		return DictWriter(open(output_file, "a"), fieldnames=fields)
	else:
		w = DictWriter(open(output_file, "w"), fieldnames=fields)
		w.writeheader()
		return w

def element_extras(extras, elem_dict):
		
	for row in extras:
			
		temp_dict = copy(elem_dict)
			
		e_name = row.keys()[0]
		temp_dict[e_name] = row[e_name]["val"]
			
		if len(row[e_name]["attributes"]) > 0:
			for attr in row[e_name]["attributes"]:
				temp_dict[e_name + "_" + attr] = row[e_name]["attributes"][attr]
			
		yield temp_dict

def process_sub_elems(elem, elem_fields):
	elem_dict = dict.fromkeys(elem_fields, '')
	elem_dict["id"] = elem.get("id")
			
	sub_elems = elem.getchildren()
	extras = []
		
	for sub_elem in sub_elems:

		if sub_elem.tag.endswith("address"):
				
			add_elems = sub_elem.getchildren()
			
			for add_elem in add_elems:
				elem_dict[sub_elem.tag + "_" + add_elem.tag] = add_elem.text
		
		elif len(elem_dict[sub_elem.tag]) > 0:
			extras.append({sub_elem.tag:{"val":sub_elem.text, "attributes":sub_elem.attrib}}) 
		else:
			elem_dict[sub_elem.tag] = sub_elem.text

	return elem_dict, extras

def process_db_sub_elems(elem, elem_fields):
	elem_dict = dict.fromkeys(elem_fields[elem.tag], '')
	elem_dict["id"] = elem.get("id")

	sub_elems = elem.getchildren()
	extras = [] 

	for sub_elem in sub_elems:
		sub_name = sub_elem.tag
		if sub_name.endswith("address"):
			add_elems = sub_elem.getchildren()
			for add_elem in add_elems:
				elem_dict[sub_name + "_" + add_elem.tag] = add_elem.text
		elif sub_name not in elem_dict:
			table_name = elem.tag + "_" + sub_name[:sub_name.find("_id")]
			extra = {"table":table_name, "elements":dict.fromkeys(elem_fields[table_name])}
			extra["elements"][elem.tag + "_id"] = elem.get("id")
			extra["elements"][sub_name] = sub_elem.text
			attributes = sub_elem.attrib
			for a in attributes:
				extra["elements"][a] = attributes[a]
			extras.append(extra)
		else:
			elem_dict[sub_name] = sub_elem.text
	return elem_dict, extras

def feed_to_element_files(output_directory, feed_file, element_props, version):
	with open(feed_file) as xml_doc:
		context = etree.iterparse(xml_doc, events=("start", "end"))
		context = iter(context)

		event, root = context.next()
		feed_version = root.attrib["schemaVersion"]
		if feed_version != version:
			print "version error"
		
		e_name = ""

		for elem in extract_base_elements(context, element_props.keys()):
			if elem.tag != e_name:
			
				e_name = elem.tag
				writer = file_writer(output_directory, e_name, element_props[e_name])
		
			elem_dict, extras = process_sub_elems(elem, element_props[e_name])
		
			writer.writerow(elem_dict)

			for row_dict in element_extras(extras, elem_dict):
				writer.writerow(row_dict)	

def feed_to_db_files(directory, feed_file):
	with open(feed_file) as xml_doc:
		context = etree.iterparse(xml_doc, events=("start", "end"))
		context = iter(context)

		event, root = context.next()
		feed_version = root.attrib["schemaVersion"]
		
		sp = SchemaProps(feed_version)
		db_props = sp.full_header_data("db")
		
		e_name = ""
		for elem in extract_base_elements(context, db_props.keys()):
			if elem.tag != e_name:
			
				e_name = elem.tag
				writer = file_writer(directory, e_name, db_props[e_name])
		
			elem_dict, extras = process_db_sub_elems(elem, db_props)
			try:
				writer.writerow(elem_dict)
			except UnicodeEncodeError:
				for key in elem_dict.keys():
					if elem_dict[key]:
						elem_dict[key] = elem_dict[key].replace(u"\ufffd", "N")
						elem_dict[key] = elem_dict[key].replace(u'\xa0', "")
						elem_dict[key] = elem_dict[key].replace(u'\u201c', "N")
						elem_dict[key] = elem_dict[key].replace(u'\u201d', "N")
				writer.writerow(elem_dict)

			for extra in extras:
				temp_writer = file_writer(directory, extra["table"], db_props[extra["table"]])
				temp_writer.writerow(extra["elements"])
	if feed_version != "3.0":
		update_version(directory, feed_version)

def get_conversion(key, data):
	temp_list = []
	if key in data[0]:
		for row in data:
			if len(row[key]) > 0:
				temp_list.append([row[key], row["id"]])
	return temp_list

def write_conversion(directory, data, fname, keys):
	if not path.exists(directory + fname):
		with open(directory + fname, "w") as f:
			writer = csv.writer(f)
			writer.writerow(keys)
			writer.writerows(data)

def remove_columns(directory, fname, data, cols, bad_cols):
	with open(directory + fname, "w") as w:
		for c in bad_cols:
			if c in cols:
				cols.remove(c)
		writer = DictWriter(w, fieldnames=cols)
		writer.writeheader()
		for row in data:
			for c in bad_cols:
				if c in row:
					row.pop(c)
			writer.writerow(row)

def read_remove_cols(directory, fname, bad_cols):
	with open(directory + fname, "r") as r:
		reader = DictReader(r)
		data = list(reader)
	remove_columns(directory, fname, data, reader.fieldnames, bad_cols)

def change_cols(directory, fname, old_col, new_col):
	with open(directory + fname, "r") as r:
		reader = DictReader(r)
		data = list(reader)
	header = reader.fieldnames
	if old_col in header:
		header.remove(old_col)
		header.append(new_col)
		with open(directory + fname, "w") as w:
			writer = DictWriter(w, fieldnames=header)
			writer.writeheader()
			for row in data:
				row[new_col] = row.pop(old_col)
				writer.writerow(row)

def update_version(directory, version):

	if path.exists(directory + "campaign_issue.txt"):
		os.remove(directory + "campaign_issue.txt")
	if path.exists(directory + "campaign_statement.txt"):
		os.remove(directory + "campaign_statement.txt")
	if path.exists(directory + "ballot_response_result.txt"):
		os.remove(directory + "ballot_response_result.txt")

	if path.exists(directory + "early_vote_site.txt"):
		with open(directory + "early_vote_site.txt", "r") as r:
			reader = DictReader(r)
			data = list(reader)
			locality_ev_site = get_conversion("locality_id", data)
			state_ev_site = get_conversion("state_id", data)
			if len(locality_ev_site) > 0:
				write_conversion(directory, locality_ev_site, "locality_early_vote_site.txt", ["locality_id", "early_vote_site_id"])
			if len(state_ev_site) > 0:
				write_conversion(directory, state_ev_site, "state_early_vote_site.txt", ["state_id", "early_vote_site_id"])
		remove_columns(directory, "early_vote_site.txt", data, reader.fieldnames, ["locality_id", "state_id"])
	
	if (version == "2.3" or version == "2.2") and path.exists(directory + "locality.txt"):
		read_remove_cols(directory, "locality.txt", ["ballot_style_image_url", "polling_location_id"])
		
	if (version == "2.1" or version == "2.2") and path.exists(directory + "polling_location.txt"):
		read_remove_cols(directory, "polling_location.txt", ["name"])

	if version == "2.1" and path.exists(directory + "ballot_candidate.txt"):
		change_cols(directory, "ballot_candidate.txt", "order", "sort_order")
	if version == "2.1" and path.exists(directory + "referendum_ballot_response.txt"):
		change_cols(directory, "referendum_ballot_response.txt", "order", "sort_order")
	if version == "2.1" and path.exists(directory + "custom_ballot_ballot_response.txt"):
		change_cols(directory, "custom_ballot_ballot_response.txt", "order", "sort_order")	
