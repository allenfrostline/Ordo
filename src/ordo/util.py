import base64
import io
import warnings
from typing import Iterable

import numpy as np
from scipy.optimize import OptimizeWarning, curve_fit

INF = np.inf


def get_b64path(bytes: io.BytesIO) -> str:
    encoded = base64.b64encode(bytes).decode()
    return f"data:image/png;base64,{encoded}"


def fit_linear_prices(price1: float, price2: float, n: int) -> Iterable[float]:
    return np.linspace(price1, price2, n)


def _expon_func(x, a, b, c):
    return a * np.exp(b - x) + c


def fit_exponential_prices(
    price1: float, price2: float, price3: float, n: int
) -> Iterable[float]:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", OptimizeWarning)
        popt, _ = curve_fit(
            _expon_func,
            xdata=[0, n // 2, n - 1],
            ydata=[price1, price2, price3],
            p0=[1, 0, 0],
            bounds=([0, -np.inf, -np.inf], np.inf),
        )
    return _expon_func(range(n), *popt)
