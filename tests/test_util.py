from ordo.util import fit_exponential_prices, fit_linear_prices


def test_linear():
    values = fit_linear_prices(100, 0, 9)
    assert round(values[0]) == 100
    assert round(values[4]) == 50
    assert round(values[-1]) == 0


def test_expon():
    values = fit_exponential_prices(100, 50, 40, 9)
    print(values)
    assert round(values[0]) == 100
    assert round(values[4]) == 45
    assert round(values[-1]) == 44
