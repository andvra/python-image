
import numpy as np
import image as img
from threading import Event, Thread
from epicycles import Epicycles
from contourpoint import ContourPoint
import utils
import json
import cv2
import time
from cmath import pi
import tkinter as tk
from PIL import Image, ImageTk

done = False
image_path = utils.get_input_image_path()
img_orig = img.load_image(image_path)
img_resized = img.resize(img_orig, 600, 600)
pixel_value = img_resized[0][0]
img_bw = np.zeros(
    (img_resized.shape[0], img_resized.shape[1], 1), np.uint8)
img_bw[:] = 255
img_bw[np.where((img_resized == pixel_value).all(axis=2))] = 0
contours = img.get_contours(img_bw)
longest_contour = []
for c in contours:
    if len(c) > len(longest_contour):
        longest_contour = c
# TODO: Reduce the number of contours by straigtening the lines
img_contour = img.draw_contours(img_resized, [longest_contour])

img.show_and_wait(img_resized, "Resized " + image_path)

# Reduces the list. Original shape: (no_contours, 1, 2). New shape: (no_contours, 2)
longest_contour_as_list = list(
    map(lambda item: (item[0][0], item[0][1]), longest_contour))
# Here, we center the points around the origin (0, 0)
average_point = np.sum(longest_contour_as_list,
                       0)//len(longest_contour_as_list)
longest_contour_as_list = longest_contour_as_list-average_point
contour_points = np.array(
    list(map(lambda item: ContourPoint(item[0], item[1]), longest_contour_as_list)))
epi = Epicycles(contour_points, 10)


class GuiCircle:
    def __init__(self, x=0, y=0, r=0):
        self.x = x
        self.y = y
        self.r = r


class GuiLine:
    def __init__(self, x1=0, y1=0, x2=0, y2=0, fill="white"):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.fill = fill


class Application(tk.Frame):
    def __init__(self, width, height, image_path, master=None):
        super().__init__(master)
        self.master = master
        master.title('Epicycles')
        master.geometry(str(width)+'x'+str(height))
        master.resizable(0, 0)
        self.width = width
        self.height = height
        self.half_width = width//2
        self.half_height = height//2
        self.canvas = tk.Canvas(master, width=width, height=height, bg="gray")
        self.canvas.pack()
        # self.pack()
        self.new_objects = []
        self.current_objects = []
        self.draw_axes()
        self.draw_image()
        self.render()

    def draw_axes(self):
        self.update_line(self.half_width, 0, self.half_width,
                         self.height, "axis_vertical")
        self.update_line(0, self.half_height, self.width, self.half_height)

    def draw_image(self):
        img_reverse_color = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)
        img_array = Image.fromarray(img_reverse_color)
        img_tk = ImageTk.PhotoImage(img_array)
        # We have calculated the center of our contour. When we draw the image, we must adjust its position
        #   based on how much it differs from the center of the image.
        diff_x = img_tk.width()/2-average_point[0]
        diff_y = img_tk.height()/2-average_point[1]
        x = self.half_width+diff_x
        y = self.half_height+diff_y
        # We need to keep a reference, otherwise it will be thrown away by the garbage collector
        self.current_image = img_tk
        self.canvas.create_image(x, y, image=img_tk)

    def update_circle(self, x, y, r, tag=None):
        circle = GuiCircle(x+self.half_width, y+self.half_height, r)
        self.update_object(tag, circle)

    def update_line(self, x1, y1, x2, y2, tag=None):
        line = GuiLine(x1, y1, x2, y2)
        self.update_object(tag, line)

    def update_object(self, tag, obj):
        self.new_objects.append((tag, obj))

    def clear(self):
        self.canvas.delete("circle")
        self.current_objects = []

    def create_circle(self, x, y, r, tag):
        if tag == None:
            return self.canvas.create_oval(x-r, y-r, x+r, y+r, tags=("circle"))
        else:
            return self.canvas.create_oval(x-r, y-r, x+r, y+r, tags=("circle", tag))

    def create_line(self, x1, y1, x2, y2, fill, tag):
        if tag == None:
            return self.canvas.create_line(x1, y1, x2, y2, fill=fill, tags=("line"))
        else:
            return self.canvas.create_line(x1, y1, x2, y2, fill=fill, tags=("line", tag))

    def move_circle(self, object_id, item):
        self.canvas.coords(object_id, item.x-item.r,
                           item.y-item.r, item.x+item.r, item.y+item.r)

    def render(self):
        while len(self.new_objects) > 0:
            obj = self.new_objects.pop()
            (item_tag, item) = obj
            if(type(item) == GuiCircle):
                existing_object = None
                if item_tag != None:
                    existing_object = next(
                        (x for x in self.current_objects if x[0] == item_tag), None)
                if existing_object != None:
                    existing_object_id = existing_object[1]
                    self.move_circle(existing_object_id, item)
                else:
                    drawn_object = self.create_circle(
                        item.x, item.y, item.r, item_tag)
                    if item_tag != None:
                        self.current_objects.append((item_tag, drawn_object))
            if(type(item) == GuiLine):
                self.create_line(item.x1, item.y1, item.x2,
                                 item.y2, item.fill, item_tag)
        self.master.after(50, self.render)


def move_circles(app, epi, t=0):
    while not done:
        coord = epi.f(t)
        coord_calc = epi.get_calculated_position(t)
        x = coord.x
        y = coord.y
        app.update_circle(x, y, 50, "First circle")
        # app.update_circle(x, y, 10)
        app.update_circle(coord_calc.x,coord_calc.y,100,"Calculated circle")
        app.update_circle(coord_calc.x,coord_calc.y, 10)
        Event().wait(0.01)
        t += 0.01
        if(t > 2*pi):
            t -= 2*pi
            app.clear()


root = tk.Tk()
app = Application(800, 800, image_path, root)
thread = Thread(target=move_circles, args=(app, epi))
# Makes it possible to exit the application even when the thread is running
thread.daemon = True
thread.start()
app.mainloop()
done = True
