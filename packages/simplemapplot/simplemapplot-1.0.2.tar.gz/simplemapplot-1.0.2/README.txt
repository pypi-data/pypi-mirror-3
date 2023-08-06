=============
SimpleMapPlot
=============

This package allows you to easily create a colored map of US States or counties.  For example::

    #!/usr/bin/env python

    import simplemapplot

    dict_stateabbrev_value = {"TX":99, "WI":45, "IL":40, "AK":5}
    simplemapplot.make_us_state_map(data=dict_stateabbrev_value)

This results in a colored US state map.

Installing
============

Simply use pip::

    pip install SimpleMapPlot

Other Examples
==============

Create a colored map of some counties::

    #!/usr/bin/env python
    import simplemapplot

    dict_fips_value = {"55025":65,"14000":90,"48650":90,"48453":90,"15009":72,"05350":45,"06067":72}
    simplemapplot.make_us_county_map(
        data=dict_fips_value,
        colors=["#F1EEF6", "#D4B9DA", "#C994C7", "#DF65B0", "#DD1C77", "#980043"])

Create a colored map of some election results::
    #!/usr/bin/env python

    import simplemapplot

    dict_stateabbrev_value = {"WA":1,"CA":1,"OR":1,"NV":0,"TX":0, "WI":1, "IL":1, "AK":0}
    colors = ["#F07763","#698DC5"]
    simplemapplot.make_us_state_map(data=dict_stateabbrev_value,colors=colors)

