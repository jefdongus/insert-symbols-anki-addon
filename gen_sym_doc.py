#!/usr/bin/env python3

"""
This script generates a Markdown file for the Github wiki symbol list.
"""

from src.default_symbols import _SYMBOL_DICT

output_fname = 'docs/Symbol_List.md'

def make_TOC():
    output = '### Sections\n'
    counter = 1

    for title in _SYMBOL_DICT:
        link_name = title.replace(' ', '-') \
            .replace('(', '') \
            .replace(')', '') \
            .lower()
        output += '%d. [%s](#%s)\n' % (counter, title, link_name)
        counter += 1

    output += ('\nFor instructions on how to add your own symbols, '
        'please see the [[FAQ|FAQ]].\n\n')
    return output

def make_section(title, symbol_list):
    output = (
        '### %s\n\n'
        '| Symbol | Key |\n'
        '| --- | --- |\n'
    ) % title

    for key, val in symbol_list:
        output += ('| %s | `%s` |\n' % (val, key))

    output += '\n[Back to Top](#sections)\n'
    return output

# Write output
with open(output_fname, 'w', 
    encoding='ascii', 
    errors='xmlcharrefreplace') as out_file:

    out_file.write('<!--- Auto-generated via gen_sym_doc.py.-->\n\n')
    out_file.write(make_TOC())
    for title, symbol_list in _SYMBOL_DICT.items():
        out_file.write(make_section(title, symbol_list))
