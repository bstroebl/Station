#Station#

a QGIS plugin

A small plugin that shows a station (= distance from the start point) on a line. The plugin was created to share the code, not to have a working plugin on its own (although it works).
The idea is to have the user click on a line in the map and show the station corresponding to this click point. The following steps are performed to reach this goal:

1. find the line next to the click point (max is 5 map units, currently hard coded)
2. if there is more than one have the user choose which line to use
3. define a perpendicular line on the line through the click point
4. split the line with this perpendicular line
5. the length of the first half of the split line is the station

Currently the algorithm uses only a tiny part of the line to define the perpendicular line. Not sure what happens if a vertex is located within this part, though.
