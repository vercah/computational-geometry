# Polygon Area Calculator

This is a Python application that allows users to draw polygons on a canvas, calculate their areas, divide them into convex parts etc. The application provides a GUI implemented using the Tkinter library.

## Prerequisites

- Python 3.x
- Tkinter library (usually included with Python)
- Shapely library (for advanced geometric operations)

## Installation on Linux

1. Clone or download this repository `git clone https://github.com/vercah/computational-geometry.git`
2. Go to the project directory `cd computational-geometry`
3. Install the libraries, if needed `pip install shapely`, `pip install tkinter`

## Usage

1. Run the application from the terminal `python geometry.py`
2. Clicking into the white plane, you can manually insert points
3. Then you can calculate the area of the polygon (in case it is a simple one), wrap the points into a convex container, or divide it into convex subpolygons
4. You can also generate 50 random points, but they most probably won't form a simple polygon, so you can only wrap them
