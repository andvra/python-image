
import numpy as np
import image as img
import json
img_orig = img.load_image('images/star_small.png')
img_gray = img.get_gray(img_orig)
img_hsv = img.get_hsv(img_orig)
hsv = img.get_hsv_parts(img_hsv)
img_bw = img.get_bw(img_gray)
img_bw2 = img.get_bw(hsv[1])
contours = img.get_contours(img_bw2)
print(contours[0].shape)
print(contours[0][0])
print(contours[0][1])
print(contours[0][0][0])
print(contours[0][1][0])
x = []
for item in contours[0]:
    x.append(item[0])
print(x[0])
print(x[1])
print(type(x))
print(type(contours[0][0][0]))
img.show_and_wait(img_orig)
img.show_and_wait(img_gray)
img.show_and_wait(img_bw)
img.show_and_wait(img_bw2)
# Fortsätt med att rita ut konturerna.
# Förslag för att testa: Skapa en vit bakgrund med storleken from img_orig och rita sedan ut konturerna
#  på denna ytan (sätt pixel x/y till färg (128,255,128) eller liknande)
img.show_and_wait_with_contour(img_orig, contours[0])
img.show_and_wait_with_contour(img_bw2, contours[0])
img.show_and_wait_with_contour(img_gray, contours[0])
img.show_and_wait(hsv[0])
img.show_and_wait((hsv[0]+75) % 180)
img.show_and_wait(hsv[1])
img.show_and_wait(hsv[2])
