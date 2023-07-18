#!/usr/bin/env python
# coding: utf-8

import tkinter as tk
from tkinter import messagebox
from shapely.geometry import LineString
import numpy as np
import itertools
import random


# triangulation

def intersects_with_polygon(polygon, point_1, point_2): # returns how many times a line intersects the polygon
    intersections = 0
    for i in range(len(polygon)):
        edge_start = polygon[i]
        edge_end = polygon[(i + 1) % len(polygon)]  # polygon is closed
        if edge_start == point_1 or edge_start == point_2 or edge_end == point_1 or edge_end == point_2: # avoid points themselves
            continue    
        if check_intersection(point_1, point_2, edge_start, edge_end):
            intersections += 1
    return intersections

def check_intersection(first1, first2, second1, second2):
    first_line = LineString([first1, first2])
    second_line = LineString([second1, second2])
    if first_line.intersects(second_line):
        return True
    return False

def is_side_correct(start, end, checked, clockwise): # check using vectors and cross product
    v1 = (end[0] - start[0], end[1] - start[1]) 
    v2 = (checked[0] - start[0], checked[1] - start[1])
    cross_product = v1[0] * v2[1] - v1[1] * v2[0]
    if (cross_product < 0 and clockwise) or (cross_product > 0 and not clockwise):
        return True
    return False

def is_clockwise(polygon):
    left = 0
    right = 0
    for i in range(len(polygon)):
        if is_side_correct(polygon[i%len(polygon)], polygon[(i+2)%len(polygon)], polygon[(i+1)%len(polygon)], True):
            left += 1
        else:
            right += 1
    if left > right:
        return True
    return False        

def triangulate_polygon(polygon):
    triangles = []
    going_clockwise = False
    if is_clockwise(polygon):
        going_clockwise = True
    i = 0
    while len(polygon) > 2: # until we can't triangulate
        vi = polygon[i % len(polygon)]
        vii = polygon[(i+1) % len(polygon)]  # polygon is closed
        viii = polygon[(i+2) % len(polygon)]
        if is_side_correct(vi, viii, vii, going_clockwise):
            if not intersects_with_polygon(polygon, vi, viii) and is_line_inside(polygon, vi, viii):
                triangles.append((vi, vii, viii))
                polygon.remove(vii)
                i = 0
                continue
        if going_clockwise:
            i += 1
        else:
            i -= 1
    return triangles

def sum_triangles(triangles):
    total_area = 0
    for triangle in triangles:
        area = triangle_area(triangle)
        total_area += area
    return total_area

def triangle_area(triangle):
    x1, y1 = triangle[0]
    x2, y2 = triangle[1]
    x3, y3 = triangle[2]
    area = 0.5 * abs((x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2))) # shoelace formula
    return area


# drawing

def on_canvas_click(click):
    x = click.x
    y = click.y
    points.append((x, y))
    canvas.create_oval(x-2, y-2, x+2, y+2, fill="black")  # show the clicked point on the canvas


# finding smallest convex wrapping

def get_wrapping(points, canvas):
    upper_wrapping = []
    lower_wrapping = []
    sorted_points = sorted(points, key=lambda p: p[0])
    upper_wrapping.append(sorted_points[0])
    upper_wrapping.append(sorted_points[1])
    lower_wrapping.append(sorted_points[0])
    lower_wrapping.append(sorted_points[1])
    for i in range(len(sorted_points)-2):
        upper_wrapping.append(sorted_points[i+2])
        lower_wrapping.append(sorted_points[i+2])
        while len(upper_wrapping)>2 and not is_side_correct(upper_wrapping[-3], upper_wrapping[-1], upper_wrapping[-2], True):
            upper_wrapping.pop(-2)
        while len(lower_wrapping)>2 and not is_side_correct(lower_wrapping[-3], lower_wrapping[-1], lower_wrapping[-2], False):
            lower_wrapping.pop(-2)
    for i in range(len(lower_wrapping)-1, 0, -1):
        upper_wrapping.append(lower_wrapping[i])
    draw_wrapping(upper_wrapping, canvas)
            
def draw_wrapping(wrapping, canvas):
    if len(wrapping) > 1: # draw the polygon
        for i in range(len(wrapping)-1):
            canvas.create_line(wrapping[i], wrapping[i+1], fill="black")
        canvas.create_line(wrapping[0], wrapping[-1], fill="black")


# dividing into convex polygons

def divide(whole_polygon, my_polygon, dividers):
    inflexes = get_inflex_points(my_polygon)
    if len(inflexes) == 0: # the polygon is already convex
        return dividers
    if len(inflexes) == 1: # can connect with arbitrary point (here the second closest neighbour) (but still we have to check)
        dividers.append((inflexes[0], my_polygon[(my_polygon.index(inflexes[0])+2)%(len(my_polygon))]))
        new_polygon_1, new_polygon_2 = cut_polygon(my_polygon, dividers[-1])
        divide(whole_polygon, new_polygon_1, dividers)
        divide(whole_polygon, new_polygon_2, dividers)
        return dividers
    if len(inflexes) > 1: # connect together, the connecting line must be inside the polygon
        pairs = list(itertools.combinations(inflexes, 2)) # get all possible pairs
        for pair in pairs:
            # remove adjoining ones
            if not (my_polygon[(my_polygon.index(pair[1])+1)%(len(my_polygon))]==pair[0] or my_polygon[(my_polygon.index(pair[0])+1)%(len(my_polygon))]==pair[1]):
                if not intersects_with_polygon(my_polygon, pair[0], pair[1]):
                    if is_line_inside(my_polygon, pair[0], pair[1]):
                        dividers.append((pair[0], pair[1]))
                        new_polygon_1, new_polygon_2 = cut_polygon(my_polygon, dividers[-1])
                        divide(whole_polygon, new_polygon_1, dividers)
                        divide(whole_polygon, new_polygon_2, dividers)
                        return dividers
        # in case none of the lines goes inside the polygon
        j = 2
        next_point = my_polygon[(my_polygon.index(inflexes[0])+j)%(len(my_polygon))]
        while intersects_with_polygon(my_polygon, inflexes[0], next_point) or not is_line_inside(my_polygon, inflexes[0], next_point):
            j+=1
            next_point = my_polygon[(my_polygon.index(inflexes[0])+j)%(len(my_polygon))]
        dividers.append((inflexes[0], next_point))
        new_polygon_1, new_polygon_2 = cut_polygon(my_polygon, dividers[-1])
        divide(whole_polygon, new_polygon_1, dividers)
        divide(whole_polygon, new_polygon_2, dividers)
        return dividers
    
def is_line_inside(polygon, point_1, point_2):
    new_point_1 = (((point_1[0]+point_2[0])/2), ((point_1[1]+point_2[1])/2))
    new_point_2 = (0, 0)
    intersected = intersects_with_polygon(polygon, new_point_1, new_point_2)
    if intersected % 2 == 0:
        return False
    return True
    
def get_inflex_points(my_polygon):
    inflexes = [] # stores the inflex points from the polygon 
    going_clockwise = False
    if is_clockwise(my_polygon):
        going_clockwise = True
    for i in range(len(my_polygon)):
        if not is_side_correct(my_polygon[i], my_polygon[(i+2)%(len(my_polygon))], my_polygon[(i+1)%(len(my_polygon))], going_clockwise):
            inflexes.append(my_polygon[(i+1)%(len(my_polygon))])
    return inflexes

def cut_polygon(polygon, divider):
    new_polygon_1 = []
    new_polygon_2 = []
    if polygon.index(divider[0]) < polygon.index(divider[1]):
        for i in range(polygon.index(divider[0]), polygon.index(divider[1])+1):
            new_polygon_1.append(polygon[i])
        for i in range(polygon.index(divider[1]), len(polygon)):
            new_polygon_2.append(polygon[i])
        for i in range(0, polygon.index(divider[0])+1):
            new_polygon_2.append(polygon[i])
    else:
        for i in range(polygon.index(divider[1]), polygon.index(divider[0])+1):
            new_polygon_1.append(polygon[i])
        for i in range(polygon.index(divider[0]), len(polygon)):
            new_polygon_2.append(polygon[i])
        for i in range(0, polygon.index(divider[1])+1):
            new_polygon_2.append(polygon[i])
    return new_polygon_1, new_polygon_2


# buttons

def calculate_area(points, canvas, calculate_button, wrap_button, divide_button, output_text):
    if len(points) > 1: # draw the polygon
        for i in range(len(points)-1):
            canvas.create_line(points[i], points[i+1], fill="black")
        canvas.create_line(points[0], points[-1:], fill="black")
    canvas.unbind("<Button-1>") # stops drawing
    calculate_button.config(state=tk.DISABLED)
    wrap_button.config(state=tk.DISABLED)
    divide_button.config(state=tk.DISABLED)
    for i in range(len(points)):
        if intersects_with_polygon(points, points[i], points[(i+1)%(len(points))]):
            text = "This polygon is not simple."
            output_text.insert(tk.END, text)
            return
    triangles = triangulate_polygon(points)
    area = sum_triangles(triangles)
    text = "Area of this polygon is " + str(area) + " square pixels."
    output_text.insert(tk.END, text)

def find_wrapping(points, calculate_button, canvas):
    get_wrapping(points, canvas)
    calculate_button.config(state=tk.DISABLED)

def divide_polygon(points, canvas, output_text):
    if len(points) > 1: # draw the polygon
        for i in range(len(points)-1):
            canvas.create_line(points[i], points[i+1], fill="black")
        canvas.create_line(points[0], points[-1:], fill="black")
    canvas.unbind("<Button-1>") # stops drawing
    for i in range(len(points)):
        if intersects_with_polygon(points, points[i], points[(i+1)%(len(points))]):
            text = "This polygon is not simple."
            output_text.insert(tk.END, text)
            return
    dividers = []
    dividers = divide(points, points, dividers)
    if len(dividers)>0:
        for i in range(len(dividers)):
            canvas.create_line(dividers[i][0], dividers[i][1], fill="red")

def generate_points(canvas, num_points):
    width = canvas.winfo_width()
    height = canvas.winfo_height()
    for _ in range(num_points):
        x = random.randint(0, width)
        y = random.randint(0, height)
        points.append((x,y))
        canvas.create_oval(x-2, y-2, x+2, y+2, fill="black")
        
def close_application(window):
    window.destroy()
    
def clear_canvas(canvas, points, calculate_button, wrap_button, divide_button, output_text):
    canvas.delete("all")
    points.clear()
    canvas.bind("<Button-1>", on_canvas_click)
    calculate_button.config(state=tk.NORMAL)
    wrap_button.config(state=tk.NORMAL)
    divide_button.config(state=tk.NORMAL)
    output_text.delete("1.0", tk.END)  # clear text


if __name__ == "__main__":
    points = []
    window = tk.Tk()
    window.title("Computational Geometry")

    canvas_width = 400
    canvas_height = 300

    canvas = tk.Canvas(window, width=canvas_width, height=canvas_height, bg="white")
    canvas.grid(row=0, column=0, columnspan=3, padx=10, pady=10)
    canvas.bind("<Button-1>", on_canvas_click)

    button_frame = tk.Frame(window)
    button_frame.grid(row=1, column=0, columnspan=3, padx=5, pady=10)
    
    calculate_button = tk.Button(button_frame, text="Area", command=lambda: calculate_area(points, canvas, calculate_button, wrap_button, divide_button, output_text))
    wrap_button = tk.Button(button_frame, text="Wrap", command=lambda: find_wrapping(points, calculate_button, canvas))
    divide_button = tk.Button(button_frame, text="Divide", command=lambda: divide_polygon(points, canvas, output_text))
    generate_button = tk.Button(button_frame, text="Random", command=lambda: generate_points(canvas, 50))
    clear_button = tk.Button(button_frame, text="Clear", command=lambda: clear_canvas(canvas, points, calculate_button, wrap_button, divide_button, output_text))
    close_button = tk.Button(button_frame, text="Close", command=lambda: close_application(window))
    
    calculate_button.pack(side=tk.LEFT)
    wrap_button.pack(side=tk.LEFT)
    divide_button.pack(side=tk.LEFT)
    generate_button.pack(side=tk.LEFT)
    clear_button.pack(side=tk.LEFT)
    close_button.pack(side=tk.LEFT)

    output_text = tk.Text(window, height=5, width=30)
    output_text.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky="ew")
    window.grid_columnconfigure(0, weight=1)

    window.mainloop()

