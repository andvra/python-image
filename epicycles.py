from cmath import pi
from contourpoint import ContourPoint


class Epicycles:
    def __init__(self, points):
        self.points = points
        self.total_length = self.set_contour_distance(points)
        self.last_visited_point = 0
        self.last_t = 0

    def set_contour_distance(self, points):
        total_length = 0
        no_points = len(points)
        for i in range(0, no_points-1):
            points[i].start_distance = total_length
            total_length += points[i].distance(points[i+1])
        points[no_points-1].start_distance = total_length
        total_length += points[no_points-1].distance(points[0])
        print('Total length: ', total_length)
        return total_length

    def f(self, t):
        current_length = t*self.total_length/(2*pi)
        if self.last_t > t:
            # Reset the "last visited" when we pass 2pi (one complete iteration)
            # last_visited_point is used to improve performance by reducing
            # number of points that we need to iterate through to find our points
            self.last_visited_point = 0
        coord = ContourPoint()
        if current_length > self.points[-1].start_distance:
            # We are somewhere after the last point
            coord = self.__calculate_current_point__(
                current_length, self.points[-1], self.points[0])
        else:
            for i in range(self.last_visited_point, len(self.points)):
                if self.points[i].start_distance <= current_length and self.points[i+1].start_distance > current_length:
                    coord = self.__calculate_current_point__(
                        current_length, self.points[i], self.points[i+1])
                    break
        self.last_t = t
        return coord

    def __calculate_current_point__(self, current_length, point_start, point_end):
        diff = point_end-point_start
        # Put the "local t" on the range 0-1
        pos_t = (current_length-point_start.start_distance) / (
            self.total_length-point_start.start_distance)
        coord_x = point_start.x + pos_t * diff.x
        coord_y = point_start.y + pos_t * diff.y
        coord = ContourPoint(coord_x, coord_y)
        print("Local t: ", pos_t)
        # print('Before: ', point_start.to_string())
        # print('Current: ', coord.to_string())
        # print('After: ', point_end.to_string())
        return coord
