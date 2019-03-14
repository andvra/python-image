from cmath import pi
from contourpoint import ContourPoint
from typing import List
import scipy.integrate as integrate
import scipy.special as special
from cmath import exp


class PartOfPath:
    def __init__(self, t_start, t_end, local_function):
        self.t_start = t_start
        self.t_end = t_end
        self.local_function = local_function

    def t_is_on_part(self, t: float) -> bool:
        return (t >= self.t_start) and (t < self.t_end)


class Epicycles:
    def __init__(self, points: List[ContourPoint], number_of_circle_pairs: int):
        self.points = points
        self.total_length = self.get_total_length(points)
        self.last_visited_part_index = 0
        self.last_t = 0
        self.parts = self.init_parts(points, self.total_length)
        self.coefficients = self.__calculate_coefficients__(
            number_of_circle_pairs)

    def __calculate_coefficients__(self, number_of_circle_pairs):
        for i in range(-number_of_circle_pairs, number_of_circle_pairs + 1):
            # Denna kan förenklas stort! Integratel är additiva, dvs 
            # integratl från a till b kan delas upp som integralerna a till c 
            # pluss c till b, givet att c ligger i intervallet a till b. 
            # Vi har funktioner för varje segment längs kurvan så med
            # hjälp av dessa kan vi ta fram koefficienterna!
            a = integrate.quad(lambda t: self.f(t)*exp(1j*i*t),0,2*pi)/(2*pi)

    def init_parts(self, points: List[ContourPoint], total_length: float) -> List[PartOfPath]:
        parts = []
        no_points = len(points)
        current_length = 0
        for i in range(0, no_points-1):
            part_length, t_start, t_end, local_function = self.__init_parts__internal(
                points[i], points[i+1], current_length, total_length)
            parts.append(PartOfPath(t_start, t_end, local_function))
            current_length = current_length + part_length
        # Init the last part, closing the path
        part_length, t_start, t_end, local_function = self.__init_parts__internal(
            points[-1], points[0], current_length, total_length)
        parts.append(PartOfPath(t_start, t_end, local_function))
        return parts

    def __init_parts__internal(self, point_start: ContourPoint, point_end: ContourPoint, current_length: float, total_length: float):
        part_length = point_start.distance(point_end)
        t_start = 2*pi*current_length/total_length
        t_end = 2*pi*(current_length+part_length)/total_length
        t_range = t_end-t_start
        # We only support straight lines right now. This opens up for different shapes, such as
        #   Beziers, which we'l find in SVGs
        def local_function(t): return point_start + \
            ((t-t_start)/t_range)*(point_end-point_start)
        return part_length, t_start, t_end, local_function

    def get_total_length(self, points: List[ContourPoint]) -> float:
        total_length = 0
        no_points = len(points)
        for i in range(0, no_points-1):
            total_length += points[i].distance(points[i+1])
        total_length += points[no_points-1].distance(points[0])
        return total_length

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
