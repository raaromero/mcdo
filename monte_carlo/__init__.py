"""
Monte Carlo Diffraction Optics

Monte Carlo simulation methods for optical diffraction and propagation.
"""

__version__ = "0.1.0"
__author__ = "Roland Albert Romero"

from .core import ApertureSimulator
from .angular_spectrum import AngularSpectrumSimulator
from .richards_wolf import RichardsWolfSimulator
from . import metrics

__all__ = [
    'ApertureSimulator',
    'AngularSpectrumSimulator',
    'RichardsWolfSimulator',
    'metrics'
]
