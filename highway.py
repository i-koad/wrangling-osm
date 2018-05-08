#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  highway.py
#  



import xml.etree.cElementTree as ET
from collections import defaultdict
import pprint

PATH = "C:/Users/pel/Documents/UDAND/Proj 2_Openstreetmap/pyfiles/"
OSMFILE = "map.osm"
  
#===============================================================#
#  Helper functions to audit and clean highway=unclassified.    #
#  Applied only when 'way' tag is encountered.                  #
#===============================================================#

def is_unclassified(elem):
	"""
		Checks if 'highway=unclassified' exists in child tag element
		
		Args:
			elem (object): ElementTree object representing child XML element
			
		Returns:
			bool: True if 'highway=unclassified' 
	"""
	
    return elem.attrib['v'] == 'unclassified'

def update_highway():
	"""Returns the desired string to update the element attribute"""
    return 'road'

def audit_highway(tag_element, default_tag_type='regular'):
	"""
		Audits XML child element for occurance of 'highway=unclassified' and
		rectifies
		
		Args:
			tag_element (object): ElementTree object representing child XML element
			default_tag_type (string): string to use when tag's 'k' attribute does 
					not contain colon
		
		Returns:
			dict: dictionary according to wanted structure
	"""
    tag_fields = {}
    if is_unclassified(tag_element):
        tag_fields['key'] = tag_element.attrib['k']
        tag_fields['value'] = update_highway()  # Change unclassified => road
        tag_fields['type'] = default_tag_type
        
    else:  # Store values as they are
        tag_fields['key'] = tag_element.attrib['k']
        tag_fields['value'] = tag_element.attrib['v']
        tag_fields['type'] = default_tag_type

    return tag_fields


#===============================#
#        Main function          #
#===============================#
def count_v(filename, k):
	"""
		Collects the occurance of 'v=*' given a specified 'k' value 
		
		Args:
			filename (object): file object containing OSM XML dataset
			k (string): string to search in attribute 'k' value
		
		Returns:
			dict: dictionary containing the various values of attribute 'v' and
					the frequency / occurance count of each value
	"""
    osm_file = open(filename, 'r')

    v = {}

    for event, elem in ET.iterparse(osm_file):
        if elem.tag == 'tag' and elem.attrib['k'] == k:
            if elem.attrib['v'] in v.keys():
                v[elem.attrib['v']] += 1
            else:
                v[elem.attrib['v']] = 1
    
    return v


def audit(osmfile):
	"""
		Audit the XML file for 'highway' tag and uncover the various values, i.e.
		for 'highway=*', list the various values represented by '*'.
		
		Args:
			osmfile (object): file object containing the OSM XML data
	"""
    unclassified_id = []
    
    # Audit the highway types
    # For highway=*, output the various types 
    v = count_v(osmfile, 'highway')
    print("There are {} different classification under the 'highway' tag:").format(len(v))
    pprint.pprint(v)
    print("\n")
    
    osm_file = open(osmfile, "r")
    for event, elem in ET.iterparse(osm_file, events=("end",)):
        if elem.tag == "way":
            for el in elem.iter('tag'):
                tag_fields = audit_highway(el)
                if tag_fields['value'] == 'road':
                    unclassified_id.append(elem.attrib['id'])
    
    print("{} entries are now 'highway=road' (including those converted \
from 'unclassified'. Way IDs are listed below:").format(len(unclassified_id))
    pprint.pprint(unclassified_id)
    
    osm_file.close()

if __name__ == '__main__':
    osm = OSMFILE
    print("Processing file ==>  {}\n").format(osm)
    audit(osm)
