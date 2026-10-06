#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 23 14:48:35 2026

@author: ericvanderlinden
"""
import os
from csvw_functions import create_annotated_table_group, create_rdf
from rdflib import Graph

# PATH_PRODUCTS="../retro/heinsius/heinsius_01_GS158/products/"
# PROJECT = 'heinsius'
# BOOK = '{}_GS{}'.format("01","158")

p = os.getcwd()
workspace = os.getenv("GITHUB_WORKSPACE", "..")
GROUP = "retro"
SERIES = "heinsius"
BOOK = "heinsius_01_GS158"
JSON_URL =  https://raw.githubusercontent.com/ericvanderlinden/resources/main/retro/heinsius/heinsius_01_GS158/dataset/csvw/heinsius_01_GS158_by_page.json

OUTPUT_PRODUCTS = os.path.join(workspace, "{}/{}/{}/products".format(GROUP,SERIES,BOOK))


# 1. Compile the CSV and JSON metadata into an annotated table group
# (Can point to local file paths or URLs)

annotated_group = create_annotated_table_group(
    input_file_path_or_url=JSON_URL
)

# 2. Convert to RDF (supports 'standard' or 'minimal' CSVW modes)\n,
rdf_ntriples = create_rdf(annotated_group, mode="standard")
# print(rdf_ntriples)

# 3. Load into rdflib to serialize into your preferred format (e.g., Turtle)
g = Graph()
g.parse(data=rdf_ntriples, format="ntriples")
#print(g.serialize(format="turtle"))
turtle_output = g.serialize(format="turtle")

with open("{}/{}_by_page.ttl".format(OUTPUT_PRODUCTS,BOOK), "w", encoding="utf-8") as ttlfile:
    ttlfile.write(turtle_output)
