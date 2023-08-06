===========
SimpleMapPlot
===========

This package allows you to easily create a colored map of US States or counties.  For example::

    #!/usr/bin/env python

    import simplemapplot

    dict_stateabbrev_value = {"TX":99, "WI":45, "IL":40, "AK":5}
    simplemapplot.make_us_state_map(data=dict_stateabbrev_value)

This results in a colored US state map.

Installing
=========

Simply use pip::

    pip install SimpleMapPlot

Other Examples
=========

Coloring US counties::

    #!/usr/bin/env python
    import simplemapplot

    dict_fips_value = {"48453":90,"15009":45}
    simplemapplot.make_us_county_map(data=dict_fips_value)