from lxml import etree
import urllib
import copy

INDICATORS = ["all", "sequence", "choice"]
TYPES = ["simpleType", "complexType"]
CONTENT = ["simpleContent"]

#TODO:Schema iterator
#TODO:Write function to get element/parent combos based on attributes

class Schema:

	def __init__(self, schemafile):

		xmlparser = etree.XMLParser(remove_comments=True)
		self.schema = self.create_schema(etree.parse(schemafile, xmlparser))
	
	def create_schema(self, schema_data):
		def getXSVal(element): #removes namespace
			try:
				return element.tag.split('}')[-1]
			except:
				return None

		def get_simple_type(element):
			return {
				"name": element.get("name"),
				"restriction": element.getchildren()[0].attrib,
				"elements": [ e.get("value") for e in element.getchildren()[0].getchildren() ]
			}
		
		def get_simple_content(element):
			return {
				"simpleContent": {
					"extension": element.getchildren()[0].attrib,
					"attributes": [ a.attrib for a in element.getchildren()[0].getchildren() ]
				}
			}

		def get_elements(element):
			if len(element.getchildren()) == 0:
				return element.attrib
	
			data = {}
	
			ename = element.get("name")
			tag = getXSVal(element)

			if ename is None:
				if tag == "simpleContent":
					return get_simple_content(element)
				elif tag in INDICATORS:
					data["indicator"] = tag
				elif tag in TYPES:
					data["type"] = tag
				else:
					data["option"] = tag

			else:
				if tag == "simpleType":
					return get_simple_type(element)
				else: 
					data.update(element.attrib)
			
			data["elements"] = []
			data["attributes"] = []
	
			for child in element.getchildren():
				if child.get("name") is not None:
					data[getXSVal(child)+"s"].append(get_elements(child))
				elif tag in INDICATORS and getXSVal(child) in INDICATORS:
					data["elements"].append(get_elements(child.getchildren()[0]))
				else:
					data.update(get_elements(child))

			if len(data["elements"]) == 0:
				del data["elements"]
			if len(data["attributes"]) == 0:
				del data["attributes"]
			
			return data

		schema = {}
		root = schema_data.getroot()
		self.version = root.attrib["version"]
		
		for child in root.getchildren():
			c_type = getXSVal(child)
			if child.get("name") is not None and not c_type in schema:
				schema[c_type] = []
			schema[c_type].append(get_elements(child))
		#		schema.setdefault(c_type,[]).append(get_elements(child))
		return schema

	def get_types(self, t_name):
		types = []
		for t in self.schema[t_name]:
			types.append(t["name"])
		return types

	def get_simpleTypes(self): 
		return self.get_types("simpleType")

	def get_complexTypes(self):
		return self.get_types("complexType")

	def matching_elements(self, element, attribute_name, attribute):
		
		element_list = []
		if attribute_name in element and element[attribute_name] == attribute and "name" in element:
			element_list.append(element["name"])
		
		if "elements" in element:
			for i in range(len(element["elements"])):
				element_list.extend(self.matching_elements(element["elements"][i], attribute_name, attribute))

		return element_list
	
	def get_elements_of_attribute(self, attribute_name, attribute):
		
		element_list = []
	
		for i in range(len(self.schema["element"])):
			element_list.extend(self.matching_elements(self.schema["element"][i], attribute_name, attribute))
		
		return list(set(e for e in element_list if e != None))

	def get_schema_match(self, sub_schema, name):

		if "name" in sub_schema and sub_schema["name"] == name:
			return sub_schema
		elif "elements" in sub_schema:
			for i in range(len(sub_schema["elements"])):
				new_schema = self.get_schema_match(sub_schema["elements"][i], name)
				if new_schema is not None:
					return new_schema

	def get_sub_schema(self, name): 

		type_list = ["element", "complexType", "simpleType"]

		for e_type in type_list:
			for i in range(len(self.schema[e_type])):
				new_schema = self.get_schema_match(self.schema[e_type][i], name)
				if new_schema is not None:
					return new_schema

	def get_attributes(self, attributes, name):
		if "name" in attributes and attributes["name"] == name:
			if "elements" in attributes:
				clean_attributes = copy.copy(attributes)
				clean_attributes["elements"] = len(attributes["elements"])
				return clean_attributes
			return attributes 
		elif "elements" in attributes:
			for i in range(len(attributes["elements"])):
				element_attributes = self.get_attributes(attributes["elements"][i], name)
				if element_attributes is not None:
					return element_attributes 
	
	def get_element_attributes(self, name): 

		type_list = ["element", "complexType"]
		
		for e_type in type_list:
			for i in range(len(self.schema[e_type])):
				attributes = self.get_attributes(self.schema[e_type][i], name)
				if attributes is not None:
					return attributes 

	def element_under_parent_attributes(self, attributes, parent_list, parent, name):
		if "name" in attributes and attributes["name"] == name and parent in parent_list:
			if "elements" in attributes:
				clean_attributes = copy.copy(attributes)
				clean_attributes["elements"] = len(attributes["elements"])
				return clean_attributes
			return attributes 
		elif "elements" in attributes:
			if "name" in attributes:
				new_parent_list = copy.copy(parent_list)
				new_parent_list.append(attributes["name"])
			for i in range(len(attributes["elements"])):
				element_attributes = self.element_under_parent_attributes(attributes["elements"][i], new_parent_list, parent, name)
				if element_attributes is not None:
					return element_attributes 

	def get_element_under_parent(self, parent, name):
		
		type_list = ["element", "complexType"]
		
		for e_type in type_list:
			for i in range(len(self.schema[e_type])):
				attributes = self.element_under_parent_attributes(self.schema[e_type][i], [], parent, name)
				if attributes is not None:
					return attributes 


	def element_list(self, sub_schema, name):
		if "name" in sub_schema and sub_schema["name"] == name and "elements" in sub_schema:
			element_list = []
			for i in range(len(sub_schema["elements"])):
				if "name" in sub_schema["elements"][i]:
					element_list.append(sub_schema["elements"][i]["name"])
			return element_list
		elif "elements" in sub_schema:
			for i in range(len(sub_schema["elements"])):
				element_list = self.element_list(sub_schema["elements"][i], name)
				if element_list is not None:
					return element_list

	def simple_list(self, sub_schema, name):
		if "name" in sub_schema and sub_schema["name"] == name and "elements" in sub_schema:
			element_list = []
			for i in range(len(sub_schema["elements"])):
				element_list.append(sub_schema["elements"][i])
			return element_list

	def get_element_list(self, schema_type, name):
		for i in range(len(self.schema[schema_type])):
			if schema_type != "simpleType":
				elements = self.element_list(self.schema[schema_type][i], name)
			else:
				elements = self.simple_list(self.schema[schema_type][i],name)
			if elements is not None:
				return elements
			

if __name__ == '__main__':
	fschema = urllib.urlopen("https://github.com/votinginfoproject/vip-specification/raw/master/vip_spec_v4.0.xsd")
#	fschema = open("../demo_data/schema.txt")

	schema = Schema(fschema)
	print schema.schema

	simples = schema.get_simpleTypes()
	print schema.get_simpleTypes()
	print schema.get_complexTypes()
	
	print schema.get_elements_of_attribute("indicator", "all")

	print schema.get_sub_schema("vip_id")

	print schema.get_element_attributes("source")
	print schema.get_element_attributes("feed_contact_id")

	print schema.get_element_list("element", "source")
	print schema.get_element_list("complexType", "simpleAddressType")

	for simple in simples:
		print schema.get_element_list("simpleType", simple)

	print schema.get_element_under_parent("precinct_split","polling_location_id")
	print schema.get_element_under_parent("contest","electoral_district_id")
	print schema.get_element_under_parent("source","electoral_district_id")

	print schema.schema["simpleType"]
	print schema.schema["complexType"]

	simpleContents = {}
	for elem in schema.schema["element"][0]["elements"]:
		for e in elem["elements"]:
			if "simpleContent" in e:
				if e["name"] in simpleContents:
					simpleContents[e["name"]]["parents"].append(elem['name'])
				else:
					simpleContents[e["name"]] = {"parents":[elem['name']]}
	print simpleContents

	e_p_with_attr = {}
	for elem in schema.schema["element"][0]["elements"]:
		for e in elem["elements"]:
			if "maxOccurs" in e and "simpleContent" not in e and e["maxOccurs"] == "unbounded":
				if e["name"] in e_p_with_attr:
					e_p_with_attr[e["name"]]["parents"].append(elem["name"])
				else:
					e_p_with_attr[e["name"]] = {"parents":[elem["name"]]}
	print e_p_with_attr
	#also could write a combo on the front end of get_simpleTypes() and get_elements_of_type() using each of the simple types

	print "custom_ballot: " + str(schema.get_sub_schema("custom_ballot"))
	print schema.get_sub_schema("ballot")
	print schema.get_sub_schema("source")
	print schema.get_sub_schema("referendum")

	print schema.get_element_under_parent("source", "attributes")
