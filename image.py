import cv2
from matplotlib import pyplot as plt


def load_image(path):
    return cv2.imread(path)


def get_gray(img_orig):
    return cv2.cvtColor(img_orig, cv2.COLOR_BGR2GRAY)


def get_hsv(img_orig):
    return cv2.cvtColor(img_orig, cv2.COLOR_BGR2HSV)


def get_hsv_parts(img_hsv):
    return cv2.split(img_hsv)


def get_bw(img_gray):
    # First, apply a Gaussian blur of size 5x5
    blur = cv2.GaussianBlur(img_gray, (5, 5), 0)
    ret, th = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    return th


def merge_bws(img_bw_1, img_bw_2):
    return cv2.bitwise_or(img_bw_1, img_bw_2)


def resize(img, max_height, max_width):
    dim = None
    (img_height, img_width) = img.shape[:2]
    ratio_image = img_height/img_width
    ratio_window = max_height/max_width
    # We should scale based on the width if the height-to-width ratio is biggest in the original image
    # Otherwise, we should do it based on height
    if ratio_image > ratio_window:
        new_width = int(float(max_height)*(1/ratio_image))
        dim = (new_width, max_height)
    else:
        new_height = int(float(max_width)*ratio_image)
        dim = (max_width, new_height)
    resized = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)

    return resized


def show(img, title="Image without title"):
    cv2.imshow(title, img)


def show_and_wait(img, title="Image without title"):
    show(img, title)
    cv2.waitKey(0)


def show_and_wait_with_contour(img, contours):
    cv2.drawContours(img, contours, -1, (128, 128, 128), 15)
    cv2.waitKey(0)


def draw_contours(img, contours):
    img_contour = img.copy()
    cv2.drawContours(img_contour, contours, -1, (32, 64, 255), 5)
    return img_contour


def hist(img):
    plt.plot()
    plt.hist(img)
    plt.show()


def plot(whatever):
    plt.plot(whatever)
    plt.show()


def get_contours(img_bw):
    contours, hierarchy = cv2.findContours(
        img_bw, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    return contours


def min_max_pixel(img):
    minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(img)
    return minVal, maxVal, minLoc, maxLoc


def copy_image(img):
    return img.copy()
