#!/usr/bin/env python
"""
Lame tests, please ignore
"""

import re

fdi = open('pdf.js', 'r')
old_soup = fdi.read()
soup = old_soup[:]
print soup[:300]
fdi.close()

fdo = open('pdf.min.js', 'w')

# Strip comments
soup = re.sub(
    '(/\*([^*]|[\r\n]|(\*+([^*/]|[\r\n])))*\*+/)|(//.*)',
    '', soup)
# remove tabs
soup = re.sub('\\t', '', soup)
soup = re.sub(': ', ':', soup)
# remove multiple spaces
soup = re.sub(' +', ' ', soup)
# remove newlines
soup = re.sub('\\n', '', soup)

# Optimize
soup = re.sub(' \|\| ', '\|\|', soup)
soup = re.sub(' = ', '=', soup)
soup = re.sub(' : ', ':', soup)
soup = re.sub(' / ', '/', soup)
soup = re.sub(' + ', '+', soup)
soup = re.sub(' - ', '-', soup)
soup = re.sub('; ', ';', soup)
soup = re.sub(' \? ', '?', soup)
soup = re.sub(', ', ',', soup)
soup = re.sub(' {', '{', soup)
soup = re.sub('{ ', '{', soup)
soup = re.sub(' }', '}', soup)
soup = re.sub('} ', '}', soup)

fdo.write(soup)
print
print soup[:300]
fdo.close()
