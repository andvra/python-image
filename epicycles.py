from image import ContourPoint, Contour
from typing import List
import scipy.integrate as integrate
from cmath import exp, cos, sin, pi


class EpiCircle:
    def __init__(self, x, y, r):
        self.x = x
        self.y = y
        self.r = r


class Epicycles:
    def __init__(self, contour: Contour, number_of_circle_pairs: int):
        self.number_of_circle_pairs = number_of_circle_pairs
        self.total_length = contour.total_length
        self.parts = contour.parts[:]
        for idx in range(0, len(self.parts)):
            self.parts[idx].invert_vertical()
        self.coefficients = self.__calculate_coefficients__(
            number_of_circle_pairs)

    def __calculate_coefficients__(self, number_of_circle_pairs):
        ret = []
        for circle_index in range(-number_of_circle_pairs, number_of_circle_pairs+1):
            real = 0
            imag = 0
            k = circle_index
            for part_index in range(0, len(self.parts)):
                cur_part = self.parts[part_index]
                v = cur_part.point_start.x
                w = (cur_part.point_end.x-cur_part.point_start.x) / \
                    self.total_length
                p = cur_part.point_start.y
                q = (cur_part.point_end.y-cur_part.point_start.y) / \
                    self.total_length
                if k == 0:
                    valReal, err = integrate.quad(lambda t: (
                        1/(2*pi))*(v+w*t), cur_part.t_start, cur_part.t_end)
                    valImag, err = integrate.quad(lambda t: (
                        1/(2*pi))*(p+q*t), cur_part.t_start, cur_part.t_end)
                else:
                    def f_real(t): return sin(-k*t)*(p+q/k**2)-cos(-k*t) * \
                        (v+w/k**2)-q*t*cos(-k*t)/k-w*t*sin(-k*t)/k
                    def f_imag(t): return sin(-k*t)*(v+w/k**2)+cos(-k*t) * \
                        (p+q/k**2)+w*t*cos(-k*t)/k-q*t*sin(-k*t)/k
                    valReal, err = integrate.quad(lambda t: f_real(
                        t), cur_part.t_start, cur_part.t_end)
                    valImag, err = integrate.quad(lambda t: f_imag(
                        t), cur_part.t_start, cur_part.t_end)
                real += valReal
                imag += valImag
            ret.append(complex(real/(2*pi), imag/(2*pi)))
            print("Done calculating circle with k=" + str(k))
        return ret

    def get_calculated_position(self, t: float):
        coord = ContourPoint()
        for k in range(-self.number_of_circle_pairs, self.number_of_circle_pairs+1):
            idx = k + self.number_of_circle_pairs
            val = self.coefficients[idx] * exp(-1j*k*t)
            coord.x -= val.real
            # Negative since we want to map a coord on the complex plane to the "UI plane".
            # UI stars with (0,0) in the upper-left corner and (0,y_max) in the bottom-left corner
            # Here, we flip it. We take care of centering when rendering
            coord.y += val.imag
        return coord

    """Return the center position and the radius of each circle, in order they should be drawn"""

    def get_circles(self, t: float) -> List[EpiCircle]:
        ret = []
        if self.number_of_circle_pairs > 0:
            c = self.coefficients[self.number_of_circle_pairs]
            for i in range(1, self.number_of_circle_pairs+1):
                coord_pos = self.coefficients[self.number_of_circle_pairs+i] * \
                    exp(-1j*i*t)
                # TODO: Check if __abs__ really does what we want?
                r = coord_pos.__abs__()
                ret.append(EpiCircle(-c.real, c.imag, r))
                c = c + coord_pos
                coord_neg = self.coefficients[self.number_of_circle_pairs-i] * \
                    exp(-1j*(-i)*t)
                r = coord_neg.__abs__()
                ret.append(EpiCircle(-c.real, c.imag, r))
                c = c + coord_neg
        return ret
