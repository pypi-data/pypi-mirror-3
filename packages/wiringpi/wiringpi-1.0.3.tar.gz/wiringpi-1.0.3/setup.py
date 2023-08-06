#!/usr/bin/env python

from setuptools import setup, find_packages, Extension

wiringpi_module = Extension(
    '_wiringpi',
    sources=[
        'wiringpi_wrap.c',
        'WiringPi/wiringPi/wiringPi.c',
        'WiringPi/wiringPi/wiringSerial.c',
        'WiringPi/wiringPi/wiringShift.c'
    ],
)

setup(
    name = 'wiringpi',
    version = '1.0.3',
    author = "Philip Howard",
    author_email = "phil@gadgetoid.com",
    url = 'https://github.com/WiringPi/WiringPi-Python/',
    description = """A python interface to WiringPi library which allows for
    easily interfacing with the GPIO pins of the Raspberry Pi. Also supports
    i2c and SPI""",
    long_description=open('README').read(),
    ext_modules = [wiringpi_module],
    py_modules = ["wiringpi"],
    install_requires=[],
)
