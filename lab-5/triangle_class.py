from triangle_func import get_triangle_type, IncorrectTriangleSides

class Triangle:
    def __init__(self, a, b, c):
        get_triangle_type(a, b, c)   # если ошибка сразу выбросит IncorrectTriangleSides 

        self.a = a
        self.b = b
        self.c = c

    def triangle_type(self):
        return get_triangle_type(self.a, self.b, self.c)

    def perimeter(self):
        return self.a + self.b + self.c
    