# Polygon Area Calculator

This is a Python application that allows users to draw polygons on a canvas, calculate their areas, divide them into convex parts etc. The application provides a GUI implemented using the Tkinter library.

## Prerequisites

- Python 3.x
- Tkinter library (usually included with Python)
- Shapely library (for advanced geometric operations)

## Installation on Linux

1. Clone or download this repository `git clone https://github.com/vercah/computational-geometry.git`
2. Go to the project directory `cd computational-geometry`
3. Install the libraries, if needed `pip install shapely`, `apt-get install python-tk` (you might need `sudo`)

## Usage

1. Run the application from the terminal `python3 geometry.py`
2. Clicking into the white plane, you can manually insert points
3. Then you can calculate the area of the polygon (in case it is a simple one), wrap the points into a convex container, or divide it into convex subpolygons
4. You can also generate 50 random points, but they most probably won't form a simple polygon, so you can only wrap them

## Brief description of the methods

### Computing area of a simple polygon
The program first checks in which direction (clockwise or counterclockwise) the polygon was created. It then uses the ear-clipping method to triangulate the polygon. It proceeds on triplets of points, trying to form a new line between the margin points. For each new triplet, it checks if the middle point is on the right side of the line (using a vector cross-product). It further verifies that the new line does not intersect with the rest of the polygon and that it is inside the polygon. Then, it sums the areas of the obtained triangles.

### Finding the smallest wrapping
The program uses the incremental algorithm. It goes through the points ordered by their x-coordinate (left to right) and tries to connect the sorted points. It checks whether the line bends to the right with each new point. This process creates the upper wrapping. Then it does the same for the lower part and finally draws the wrapping around the points.

### Division into convex subpolygons
The program uses a recursive method to divide the polygon. First, it finds all the inflection points. Then it tries to connect the first one either to other inflection points, or (if it doesn't find suitable pair) to other vertices. During this process, it checks whether the dividing line crosses any of the edges of the polygon, and also whether it lies inside of it. When a new dividing line is found, the algorithm does the same for the two smaller polygons. This continues until the examined polygon is convex.
