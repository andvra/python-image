import cv2
from matplotlib import pyplot as plt
from cmath import sqrt, pi
from typing import List, Tuple
import numpy as np


class ContourPoint:
    """ Point class """

    def __init__(self, x: float = 0, y: float = 0, start_distance: float = 0):
        self.x = x
        self.y = y

    def __add__(self, other_point):
        return ContourPoint(self.x + other_point.x, self.y + other_point.y)

    def __sub__(self, other_point):
        return ContourPoint(self.x - other_point.x, self.y - other_point.y)

    def __mul__(self, other: float):
        return ContourPoint(self.x*other, self.y*other)

    def __rmul__(self, other: float):
        return self.__mul__(other)

    def distance(self, other_point):
        ret = sqrt((self.x - other_point.x) ** 2 +
                   (self.y - other_point.y) ** 2).real
        return ret

    def to_string(self):
        return str(self.x) + " " + str(self.y)

    def invert_vertical(self):
        self.y = -self.y


class PartOfPath:
    def __init__(self, point_start: ContourPoint, point_end: ContourPoint, t_start: float, t_end: float):
        self.point_start = point_start
        self.point_end = point_end
        self.t_start = t_start
        self.t_end = t_end

    def t_is_on_part(self, t: float) -> bool:
        return (t >= self.t_start) and (t < self.t_end)

    def invert_vertical(self):
        self.point_start.y = -self.point_start.y
        self.point_end.y = -self.point_end.y

    # We only support straight lines right now. This opens up for different shapes, such as
    #   Beziers, which we'll find in SVGs
    def local_function(self, t: float) -> ContourPoint:
        t_range = self.t_end-self.t_start
        return self.point_start + ((t-self.t_start)/t_range)*(self.point_end-self.point_start)


class Contour:
    def __init__(self, total_length: float, parts: List[PartOfPath], average_point: ContourPoint):
        self.total_length = total_length
        self.parts = parts
        self.average_point = average_point
        self.last_visited_part_index = 0
        self.last_t = 0

    def f(self, t) -> ContourPoint:
        if self.last_t > t:
            # Reset the "last visited" when we pass 2pi (one complete iteration)
            # last_visited_part is used to improve performance by reducing
            # number of parts that we need to iterate through to find our coordinate
            self.last_visited_part_index = 0
        coord = ContourPoint()
        if t > self.parts[-1].t_start:
            # We are somewhere after the last point
            coord = self.__calculate_current_coordinate__(self.parts[-1], t)
        else:
            for i in range(self.last_visited_part_index, len(self.parts)):
                if self.parts[i].t_is_on_part(t):
                    coord = self.__calculate_current_coordinate__(
                        self.parts[i], t)
                    break
        self.last_t = t
        return coord

    def __calculate_current_coordinate__(self, part: PartOfPath, t: float) -> ContourPoint:
        coord = part.local_function(t)
        coord_x = coord.x
        coord_y = coord.y
        coord = ContourPoint(coord_x, coord_y)
        return coord


def get_total_length(points: List[ContourPoint]) -> float:
    total_length = 0
    no_points = len(points)
    for i in range(0, no_points-1):
        total_length += points[i].distance(points[i+1])
    total_length += points[no_points-1].distance(points[0])
    return total_length


def get_parts(points: List[ContourPoint], total_length: float) -> List[PartOfPath]:
    parts = []
    no_points = len(points)
    current_length = 0
    for i in range(0, no_points-1):
        part_length, t_start, t_end = __get_parts__internal(
            points[i], points[i+1], current_length, total_length)
        parts.append(PartOfPath(
            points[i], points[i+1], t_start, t_end))
        current_length = current_length + part_length
    # Init the last part, closing the path
    part_length, t_start, t_end = __get_parts__internal(
        points[-1], points[0], current_length, total_length)
    parts.append(PartOfPath(
        points[-1], points[0], t_start, t_end))
    return parts


def __get_parts__internal(point_start: ContourPoint, point_end: ContourPoint, current_length: float, total_length: float):
    part_length = point_start.distance(point_end)
    t_start = 2*pi*current_length/total_length
    t_end = 2*pi*(current_length+part_length)/total_length
    t_range = t_end-t_start

    return part_length, t_start, t_end


def load_image_2(image_path: str, max_height: int, max_width: int) -> Tuple[np.ndarray, Contour]:
    last_dot_idx = image_path.rfind(".")
    file_type = image_path[last_dot_idx+1:]
    if file_type == "svg":
        # TODO
        a = 3
    else:
        img_orig = load_image(image_path)
        img_resized = resize(img_orig, max_height, max_width)
        pixel_value = img_resized[0][0]
        img_bw = np.zeros(
            (img_resized.shape[0], img_resized.shape[1], 1), np.uint8)
        img_bw[:] = 255
        img_bw[np.where((img_resized == pixel_value).all(axis=2))] = 0
        contours = get_contours(img_bw)
        longest_contour = []
        for c in contours:
            if len(c) > len(longest_contour):
                longest_contour = c
        # TODO: Reduce the number of contours by straigtening the lines with some error margin

        # Reduces the list. Original shape: (no_contours, 1, 2). New shape: (no_contours, 2)
        longest_contour_as_list = list(
            map(lambda item: (item[0][0], item[0][1]), longest_contour))
        # Here, we center the points around the origin (0, 0)
        ap = np.sum(longest_contour_as_list,
                    0)//len(longest_contour_as_list)
        average_point = ContourPoint(ap[0], ap[1])

        longest_contour_as_list = longest_contour_as_list-ap
        contour_points = np.array(
            list(map(lambda item: ContourPoint(item[0], item[1]), longest_contour_as_list)))
        total_length = get_total_length(contour_points)
        parts = get_parts(contour_points, total_length)
        contour = Contour(total_length, parts, average_point)
        return img_resized, contour


def load_image(path: str) -> np.ndarray:
    return cv2.imread(path)


def get_gray(img_orig: np.ndarray):
    return cv2.cvtColor(img_orig, cv2.COLOR_BGR2GRAY)


def get_hsv(img_orig: np.ndarray):
    return cv2.cvtColor(img_orig, cv2.COLOR_BGR2HSV)


def get_hsv_parts(img_hsv: np.ndarray):
    return cv2.split(img_hsv)


def get_bw(img_gray: np.ndarray):
    # First, apply a Gaussian blur of size 5x5
    blur = cv2.GaussianBlur(img_gray, (5, 5), 0)
    ret, th = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    return th


def merge_bws(img_bw_1: np.ndarray, img_bw_2: np.ndarray):
    return cv2.bitwise_or(img_bw_1, img_bw_2)


def resize(img: np.ndarray, max_height: int, max_width: int) -> np.ndarray:
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


def show(img: np.ndarray, title: str = "Image without title"):
    cv2.imshow(title, img)


def show_and_wait(img: np.ndarray, title: str = "Image without title"):
    show(img, title)
    cv2.waitKey(0)


def show_and_wait_with_contour(img: np.ndarray, contours):
    cv2.drawContours(img, contours, -1, (128, 128, 128), 15)
    cv2.waitKey(0)


def draw_contours(img: np.ndarray, contours):
    img_contour = img.copy()
    cv2.drawContours(img_contour, contours, -1, (32, 64, 255), 5)
    return img_contour


def hist(img: np.ndarray):
    plt.plot()
    plt.hist(img)
    plt.show()


def plot(whatever):
    plt.plot(whatever)
    plt.show()


def get_contours(img_bw: np.ndarray):
    contours, hierarchy = cv2.findContours(
        img_bw, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    return contours


def min_max_pixel(img: np.ndarray):
    minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(img)
    return minVal, maxVal, minLoc, maxLoc


def copy_image(img: np.ndarray):
    return img.copy()
