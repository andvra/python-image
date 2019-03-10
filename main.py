
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

done = False
image_path = utils.get_input_image_path()
img_orig = img.load_image(image_path)
img_resized = img.resize(img_orig, 700, 700)
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
print('Longest contour is contains ', len(longest_contour), ' points')
# TODO: Reduce the number of contours by straigtening the lines
img_contour = img.draw_contours(img_resized, [longest_contour])

# img.show_and_wait(img_resized, "Resized " + image_path)
# img.show_and_wait(img_bw, "BW")
# img.show_and_wait(img_contour, "Contour")

# Reduces the list. Original shape: (no_contours, 1, 2). New shape: (no_contours, 2)
contour_points = np.array(
    list(map(lambda item: ContourPoint(item[0][0], item[0][1]), longest_contour)))
epicycles = Epicycles(contour_points)
# print('0: ', epicycles.f(0).to_string())
# print('1: ', epicycles.f(1).to_string())
# print('2: ', epicycles.f(2).to_string())
# print('3.1415: ', epicycles.f(3.1415).to_string())
# print('6: ', epicycles.f(6).to_string())
# print('6.283: ', epicycles.f(6.283).to_string())


class GuiCircle:
    def __init__(self, x=0, y=0, r=0):
        self.x = x
        self.y = y
        self.r = r


class Application(tk.Frame):
    def __init__(self, width, height, master=None):
        super().__init__(master)
        self.master = master
        master.title('Epicycles')
        master.geometry(str(width)+'x'+str(height))
        master.resizable(0, 0)
        self.canvas = tk.Canvas(master, width=width, height=height, bg="gray")
        self.canvas.pack()
        # self.pack()
        self.new_objects = []
        self.current_objects = []
        self.render()

    def update_circle(self, x, y, r, tag=None):
        circle = GuiCircle(x, y, r)
        self.update_object(tag, circle)

    def update_object(self, tag, obj):
        self.new_objects.append((tag, obj))

    def create_circle(self, x, y, r, tag):
        if tag == None:
            return self.canvas.create_oval(x-r, y-r, x+r, y+r, tags=("circle"))
        else:
            return self.canvas.create_oval(x-r, y-r, x+r, y+r, tags=("circle", tag))

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
        self.master.after(50, self.render)


def move_circles(app, x=0, y=0):
    app.update_circle(x, y, 50, "First circle")
    x += 1
    y += 2
    Event().wait(0.05)
    if not done:
        move_circles(app, x, y)


root = tk.Tk()
app = Application(800, 600, root)
thread = Thread(target=move_circles, args=[app])
# Makes it possible to exit the application even when the thread is running
thread.daemon = True
thread.start()
app.mainloop()
done = True
