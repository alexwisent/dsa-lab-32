class IncorrectTriangleSides(Exception):
    """Пользовательское исключение для некорректных сторон треугольника"""
    pass


def get_triangle_type(a, b, c):
    if not (isinstance(a, (int, float)) and
            isinstance(b, (int, float)) and
            isinstance(c, (int, float))):
        raise IncorrectTriangleSides("Все стороны должны быть числами")

    if a <= 0 or b <= 0 or c <= 0:
        raise IncorrectTriangleSides("Стороны должны быть положительными числами")

    if a + b <= c or a + c <= b or b + c <= a:
        raise IncorrectTriangleSides("Нарушено неравенство треугольника")

    if a == b == c:
        return "equilateral"    # равносоторонний - все три стороны равны
    elif a == b or a == c or b == c:
        return "isosceles"  # равнобедренный - хотя бы две равны
    else:
        return "nonequilateral" # все стороны разные