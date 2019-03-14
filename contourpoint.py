from cmath import sqrt


class ContourPoint:
    """ Point class """

    def __init__(self, x=0, y=0, start_distance=0):
        self.x = x
        self.y = y

    def __add__(self, other_point):
        return ContourPoint(self.x + other_point.x, self.y + other_point.y)

    def __sub__(self, other_point):
        return ContourPoint(self.x - other_point.x, self.y - other_point.y)

    def __mul__(self,other:float):
        return ContourPoint(self.x*other,self.y*other)

    def __rmul__(self,other:float):
        return self.__mul__(other)

    def distance(self, other_point):
        ret = sqrt((self.x - other_point.x) ** 2 +
                   (self.y - other_point.y) ** 2).real
        return ret

    def to_string(self):
        return str(self.x) + " " + str(self.y)
