#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  streetname.py
#  



import xml.etree.cElementTree as ET
from collections import defaultdict
import pprint
import re

from highway import audit_highway


OSM_FILE = "map.osm"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')

street_type_re = re.compile(r'''\b st r? e* t? \.? $ |        # street
                                \b dr \S{,3} $ |              # drive
                                \b av e? \S{,4} $ |           # avenue
                                \b b \S* l e? v r? d? \.? $ | # boulevard
                                \b [eh] \S+ way \.? $ |       # expressway, highway
                                \b r o? a? d \.? $ |          # road
                                \b byp \S+ \.? $ |            # bypass
                                ring \s road \s? 2? $ |       # ring road, ring road 2
                                ^ j a? l a? n \.? |           # jalan
                                ^ l o? r \S* g \.? |          # lorong
                                ^ lebuh \S* |                 # lebuh, lebuhraya
                                ^ persia \S+                  # persiaran (excludes persimpangan)
                            '''
                            ,re.IGNORECASE | re.VERBOSE)


def bad_street_type(street_name, expected):
	'''
		Matches street_name against RE and checks if matched name is the expected name
		
		Args:
				street_name (string): variable to be matched against RE
				expected (list): variable with expected street names
				
		Returns:
				string: if street_name is not as expected
				boolean: False if street_name is as expected i.e not bad street name 
	'''
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            return street_type
        else:
            return False
    else:
        return False  # If no match, returns 'False' to calling function in order to continue w/o updating name

def has_addr_street(elem):
    '''
		Takes in an element and determines if "addr.street" exists in "node" & "way".
		 
		Args:
				elem (object): ElementTree object representing parent XML element
				
		Returns:
				boolean: True if "addr.street" exists
    '''
    if elem.tag == "node" or elem.tag == "way":
        for child in elem.iter('tag'):
            if child.attrib['k'] == "addr:street":  # Check if "addr:street" in "node" elements
                return True

    
def has_highway(elem):
    '''
		Takes in an element and determines if "highway" exists in "way" element. 
		
		Args:
				elem (object): ElementTree object representing parent XML element
				
		Returns:
				boolean: True if "highway" exists
    '''
    if elem.tag == "way":  
        for child in elem.iter('tag'):
            if child.attrib['k'] == "highway":  # Check if "way" element contains "highway"
                return True

    
def update_name(name, mapping):
	'''
		Correct the given street name 
		
		Args:
				name (string): street name variable to be corrected
				mapping (dict): dictionary mapping wrong name to the correct name 
				
		Returns:
				string: corrected street name
    '''
    # STEP 1 Split string in 'name' into sub-strings
    substrings = name.split()
    
    # STEP 2 Replace 1st index in 'substrings' with matching result from 'mapping'
    substrings[0] = mapping[substrings[0]]
    
    # STEP 3 Check for lower case in street name, and capitalize
    for i in range(len(substrings)):
        if substrings[i].islower():
            substrings[i] = substrings[i].capitalize()
    
    # STEP 4 Join the sub-strings and return result
    name = " ".join(substrings)

    return name

def collect_tags(tag_element, default_tag_type):
	'''
		Checks 'tag' element for colon in the attribute 'k' and 
		compiles 'tag' elements into desired structure after check
		
		Args:
				tag_element (object): ElementTree object representing child XML element
				default_tag_type (string): variable to use as default if no colon exists
						in the tag's 'k' value
						
		Returns:
				dict: dictionary containing the re-structured tag element
    '''
    tag_fields = {}
    
    # Check for colons
    if LOWER_COLON.match(tag_element.attrib['k']):  # If colon exists, perform splits
        colons = tag_element.attrib['k'].split(':', 1)  # Split the string with max-split of 1
        tag_fields['key'] = colons[1]  # Stores 2nd part of split as tag key's value
        tag_fields['type'] = colons[0]  # Stores 1st part of split as tag type's value
        tag_fields['value'] = tag_element.attrib['v']

    else:
        tag_fields['key'] = tag_element.attrib['k']
        tag_fields['type'] = default_tag_type
        tag_fields['value'] = tag_element.attrib['v']
                
    return tag_fields

def audit_streetname(elem, expected, mapping, problem_chars, default_tag_type="regular"):
	'''
		1. Checks and cleans XML element for 'addr:street' name errors and 'highway' name errors.
		2. Checks for and cleans 'highway=unclassified'. 
		3. Compiles elements into desired structure.
		
		Args:
				elem (object): ElementTree object representing parent XML element
				expected (list): variable with expected street names
				mapping (dict): dictionary mapping wrong name to the correct name
				problem_chars (object): Python RE object with criteria for 
						non-desired string characters
				default_tag_type (string): variable to use as default if no colon exists
						in the tag's 'k' value
						
		Returns:
				list: list of cleaned tags structured accordingly for export to CSV
    '''
    tags = []
    
    # Audit child element with 'addr:street' tag
    if has_addr_street(elem):  
        for tag in elem.iter("tag"):
            tag_fields = {}  # Initialize a container
            
            # Detect and audit 'addr:street'
            if tag.attrib['k'] == 'addr:street':
                tag_fields['id'] = elem.attrib['id']  # Store 'id' of top level tag
                
                # If street type is in expected list (i.e. not bad), 
                # process colon & store original name
                if not bad_street_type(tag.attrib['v'], expected):
                    # Split 'addr:street' values to 'key' and 'type'
                    colons = tag.attrib['k'].split(':', 1)  
                    tag_fields['key'] = colons[1]  
                    tag_fields['type'] = colons[0]  
                    
                    # Store original street name
                    tag_fields['value'] = tag.attrib['v']
                
                # Else, process colon & fix the street type label
                else:
                    # Split 'addr:street' values to 'key' and 'type'
                    colons = tag.attrib['k'].split(':', 1)  
                    tag_fields['key'] = colons[1]  
                    tag_fields['type'] = colons[0]  
                    
                    # Fix the street name 
                    tag_fields['value'] = update_name(tag.attrib['v'], mapping)
            
            # Detect and audit 'highway=unclassified'    
            elif tag.attrib['k'] == 'highway':
                tag_fields['id'] = elem.attrib['id']  # Store 'id' of top level tag
                    
                # Audit for highway=unclassified
                tag_fields.update(audit_highway(tag))    
           
			# Process remaining child elements
            else:
                if problem_chars.search(tag.attrib['k']) == None:  # If no problem...
                    tag_fields['id'] = elem.attrib['id']  # Store 'id' of top level tag
                    
                    # Process remaining fields 
                    tag_fields.update(collect_tags(tag, default_tag_type))
                else:
                    continue
            
            tags.append(tag_fields)     
    
    # Audit child element with 'highway' tag            
    elif has_highway(elem):
        for tag in elem.iter('tag'):
            tag_fields = {}  # Initialize a container
            
            # Look for 'name' in the case of elements containing highway=*
            if tag.attrib['k'] == 'name':  
                tag_fields['id'] = elem.attrib['id']  # Store 'id' of top level tag
                if not bad_street_type(tag.attrib['v'], expected):
                    tag_fields['key'] = tag.attrib['k']  
                    tag_fields['type'] = default_tag_type  
                    tag_fields['value'] = tag.attrib['v']  
                else:
                    tag_fields['key'] = tag.attrib['k']  
                    tag_fields['type'] = default_tag_type  
                    tag_fields['value'] = update_name(tag.attrib['v'], mapping)  # Update street name

            elif tag.attrib['k'] == 'highway':  # Otherwise check for highway=unclassified
                tag_fields['id'] = elem.attrib['id']  # Store 'id' of top level tag
                    
                # Audit for highway=unclassified
                tag_fields.update(audit_highway(tag))
            
            else:
                if problem_chars.search(tag.attrib['k']) == None:  # If no problem...
                    tag_fields['id'] = elem.attrib['id']  # Store 'id' of top level tag
                    
                    # Process remaining fields 
                    tag_fields.update(collect_tags(tag, default_tag_type))
                else:
                    continue
                    
            tags.append(tag_fields)
    
    # Audit and process remainder child elements
    else:  
        for tag in elem.iter('tag'):
            tag_fields = {}  # Initialize a container
            
            if problem_chars.search(tag.attrib['k']) == None:  # If no problem...
                    tag_fields['id'] = elem.attrib['id']  # Store 'id' of top level tag
                    
                    # Process remaining fields 
                    tag_fields.update(collect_tags(tag, default_tag_type))
            else:
                continue
                
            tags.append(tag_fields)
            
    return tags

#=====================================#
#     Main + helper function          #
#=====================================#

def check_strname(osm_file, list_id=False):
	'''
		Audits street name in OSM file for unexpected names and 
		lists each fault along with its respective street names
		
		Args:
				osm_file (object): file object containing the OSM XML dataset
				list_id (boolean): variable to control if nodes' or ways' ID will 
						be displayed
				
	'''
	expected = ["Avenue", "Bypass", "Expressway", "Highway", "Ring Road 2", "Road",   
				"Jalan", "Lebuh", "Lebuhraya", "Lorong", "Persiaran",
				"road"]
	
	elem_stat = {'total': 0,
				 'matched': 0,
				 'id': []}
	id_total = 0
	elem_matched = 0
	
	street_types = defaultdict(set)
	
	for event, elem in ET.iterparse(osm_file):
		if elem.tag == 'node' or elem.tag == 'way':
			id_total += 1
		if has_addr_street(elem) or has_highway(elem):
			elem_matched += 1
			for child in elem.iter('tag'):
				street_type = bad_street_type(child.attrib['v'], expected)
				if not street_type:  # If street_type == 'False'
					continue
				else:
					street_types[street_type].add(child.attrib['v'])
					elem_stat['id'].append(elem.attrib['id'])
		
		else:
			continue
	
	elem_stat['total'] = id_total
	elem_stat['matched'] = elem_matched
		
	pprint.pprint(dict(street_types))
	print("\nIDs processed: {} \nIDs matched: {} \nIDs with bad name: {}")\
		.format(elem_stat['total'], elem_stat['matched'], len(elem_stat['id']))
	
	if list_id:
		pprint.pprint(elem_stat['id'])
	
	print("===============================================================================")

def fix_strname(osm_file):
	'''
		Searches & fixes street name in OSM XML datafile by calling on other functions 
		
		Args:
				osm_file (object): file object containing the OSM XML dataset
				
	'''	
	problem_chars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
	
	expected = ['Jalan', 'Lebuh', 'Lebuhraya', 'Lorong', 'Persiaran',
				'Expressway', 'Highway',
				'road']
	
	mapping = {'Jln': 'Jalan',
			   'jalan': 'Jalan'}
	
	children = []
	tags = []
	
	for event, elem in ET.iterparse(osm_file):
		if has_addr_street(elem) or has_highway(elem):
			children = audit_streetname(elem, expected, mapping, problem_chars)
		else:
			continue
		
		tags.append(children)
		
	pprint.pprint(tags)
	print("\nNumber of 'way' or 'node' elements processed: {}").format(len(tags))
	
if __name__ == '__main__':

	donot_fix = True  # True = only checks street name. False = checks & fixes street name.
	
	print("\nProcessing file  ==>  {}\n").format(OSM_FILE)
	
	print("Checking OSM file for street name errors...")
	check_strname(OSM_FILE, list_id=False)
	
	if not donot_fix:
		print("\nFixing OSM file for street name errors...")
		fix_strname(OSM_FILE)
