from triangle_func import get_triangle_type, IncorrectTriangleSides

class Triangle:
    def __init__(self, a, b, c):
        get_triangle_type(a, b, c)  # проверка + выброс исключения

        self.a = a
        self.b = b
        self.c = c

    def triangle_type(self):    # передает сохраненые стороны в get_triangle_type, которая проверят и возвращает тип треугольника
        return get_triangle_type(self.a, self.b, self.c)

    def perimeter(self):    # вычсиляет и возращает перимерт 
        return self.a + self.b + self.c
    