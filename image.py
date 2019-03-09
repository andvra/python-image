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
    print(ret)
    return th


def show_and_wait(img):
    cv2.imshow("Bild", img)
    cv2.waitKey(0)


def show_and_wait_with_contour(img, contours):
    cv2.drawContours(img, contours, -1, (128, 128, 128), 15)
    cv2.waitKey(0)

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
