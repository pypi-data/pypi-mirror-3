#!/usr/bin/env python
#
# Plot data into a county-level map of the US.
# Counties in the US are determined by a FIPS code.
#
# Based on tutorial at
#   http://flowingdata.com/2009/11/12/how-to-make-a-us-county-thematic-map-using-free-tools/
#
# Michael Anderson, April 21, 2012

import os

from BeautifulSoup import BeautifulSoup

#default_colors = ["#F1EEF6", "#D4B9DA", "#C994C7", "#DF65B0", "#DD1C77", "#980043"]
default_colors = ["#F1EEF6", "#D0D1E6", "#A6BDDB", "#7FA9CF", "#2B8CBE", "#045A8D"]

svg_file_location = os.path.join(os.path.dirname(__file__), 'svg_maps/')

def make_us_county_map(
    data,
    colors=default_colors,
    min_value=None,
    max_value=None,
    output_img="output_county_map.svg"):
    '''
    Create svg image of US counties colored specifically.
    Inputs:
    data = dict where key=FIPS (county code), value=any number (determines color)
    colors = array of strings storing color codes
    '''
    if not min_value: min_value = min([data[key] for key in data]) # Counties near the min get colors[0]
    if not max_value: max_value = max([data[key] for key in data]) # Counties near the min get colors[-1]
    # Load SVG map
    svg = open(svg_file_location+'us_counties_map.svg', 'r').read()
    # Load map into Beautiful Soup
    soup = BeautifulSoup(svg, selfClosingTags=['defs','sodipodi:namedview'])
    # Find counties in the SVG map
    paths = soup.findAll('path')
    # County style
    path_style = 'fill-opacity:1;stroke:#ffffff;stroke-opacity:1;stroke-width:0.75;stroke-miterlimit:4;stroke-dasharray:none;fill:'
    # Color the counties based on dictionary data
    for p in paths:
        if p['id'] not in ["State_Lines", "separator"]:
            try:
                county_value = data[p['id']]
            except:
                continue
            color_class = int(round(
                                float(len(colors)-1)*float(county_value-min_value)/
                                float(max_value - min_value)))
            color = colors[color_class]
            p['style'] = "".join([path_style, color])
        
    # Save result into a file
    f = open(output_img, "w")
    f.writelines(soup.prettify())

def make_us_state_map(data,
    colors=default_colors,
    min_value=None,
    max_value=None,
    output_img="output_state_map.svg"):
    '''
    Create svg image of US counties colored specifically.
    Inputs:
    data = dict where key=State Abbreviation (AL, AK, AZ etc..), value=any number (determines color)
    colors = array of strings storing color codes
    '''
    if not min_value: min_value = min([data[key] for key in data]) # Counties near the min get colors[0]
    if not max_value: max_value = max([data[key] for key in data]) # Counties near the min get colors[-1]
    # Load SVG map
    svg = open(svg_file_location+'us_states_map.svg', 'r').read()
    # Load map into Beautiful Soup
    soup = BeautifulSoup(svg, selfClosingTags=['sodipodi:namedview'])
    # Find counties in the SVG map
    paths = soup.findAll('path')
    # County style
    path_style = 'stroke:#ffffff;stroke-opacity:1;stroke-width:0.75;stroke-miterlimit:4;stroke-dasharray:none;fill:'
    # Color the counties based on dictionary data
    for p in paths:
        if p['id'] not in ["path57","MI-","SP-"]:
            try:
                value = data[p['id']]
            except:
                continue
            color_class = int(round(
                                float(len(colors)-1)*float(value-min_value)/
                                float(max_value - min_value)))
            color = colors[color_class]
            p['style'] = "".join([path_style, color])
        
    # Save result into a file
    f = open(output_img, "w")
    f.writelines(soup.prettify())

if __name__ == '__main__':
    # Create Dictionary where
    #   key   = FIPS (county location)
    #   value = A number (like a rate, or a count)
    dict_fips_value = {"55025":70,"48453":90,"15009":45}
    make_us_county_map(data=dict_fips_value)
    dict_stateabbrev_value = {"TX":99, "WI":45, "IL":40, "AK":5}
    make_us_state_map(data=dict_stateabbrev_value)