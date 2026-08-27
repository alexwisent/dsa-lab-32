import pytest
from triangle_class import Triangle, IncorrectTriangleSides

# создаем фикстуры(готовыые данные/объект) с разными треугольниками 
@pytest.fixture
def equilateral():
    return Triangle(5, 5, 5)

@pytest.fixture
def isosceles():
    return Triangle(6, 6, 7)

@pytest.fixture
def nonequilateral():
    return Triangle(3, 4, 5)


# ========== ПОЗИТИВНЫЕ ТЕСТЫ ==========

# проверяется, что стороны правильно сохранились в атрибутах объекта
def test_triangle_creation_positive():  
    t = Triangle(3, 4, 5)
    assert t.a == 3
    assert t.b == 4
    assert t.c == 5

def test_equilateral_type(equilateral):
    assert equilateral.triangle_type() == "equilateral"

def test_isosceles_type(isosceles):
    assert isosceles.triangle_type() == "isosceles"

def test_nonequilateral_type(nonequilateral):
    assert nonequilateral.triangle_type() == "nonequilateral"

def test_perimeter(equilateral, isosceles, nonequilateral):
    assert equilateral.perimeter() == 15
    assert isosceles.perimeter() == 19
    assert nonequilateral.perimeter() == 12

def test_equilateral_float():
    t = Triangle(2.5, 2.5, 2.5)
    assert t.triangle_type() == "equilateral"
    assert t.perimeter() == 7.5

def test_isosceles_float():
    t = Triangle(5.5, 5.5, 6.0)
    assert t.triangle_type() == "isosceles"

def test_nonequilateral_float():
    t = Triangle(1.5, 2.0, 2.5)
    assert t.triangle_type() == "nonequilateral"
    assert t.perimeter() == 6.0


# ========== НЕГАТИВНЫЕ ТЕСТЫ ==========

def test_zero_side():
    with pytest.raises(IncorrectTriangleSides):
        Triangle(0, 5, 5)

def test_negative_side():
    with pytest.raises(IncorrectTriangleSides):
        Triangle(-3, 4, 5)

def test_all_zeros():
    with pytest.raises(IncorrectTriangleSides):
        Triangle(0, 0, 0)

def test_triangle_inequality():
    with pytest.raises(IncorrectTriangleSides):
        Triangle(1, 2, 3)
    with pytest.raises(IncorrectTriangleSides):
        Triangle(1, 1, 3)

def test_invalid_types():
    with pytest.raises(IncorrectTriangleSides):
        Triangle("5", 4, 5)
    with pytest.raises(IncorrectTriangleSides):
        Triangle(5, None, 5)
    with pytest.raises(IncorrectTriangleSides):
        Triangle([1], 2, 3)

def test_mixed_invalid():
    with pytest.raises(IncorrectTriangleSides):
        Triangle(-1, "a", 0)


if __name__ == "__main__":
    pytest.main(["-v", __file__])