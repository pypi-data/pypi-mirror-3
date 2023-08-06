#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Three sides of Mordor were bounded by mountain ranges, arranged in a rough
rectangle: Ered Lithui, translated as 'Ash Mountains' in the north, Ephel
Duath, translated as 'Fence of Shadow' in the west, and an unnamed (or was
possibly still called Ephel Duath) range in the south. In the northwest corner
of Mordor, the deep valley of Udun formed the region's gate and guard house.
That was the only entrance for large armies, and was where Sauron built the
Black Gate of Mordor, and later where Gondor built the Towers of the Teeth.
Behind the Black Gate, these towers watched over Mordor during the time of
peace between the Last Alliance and Sauron's return. In front of the Morannon
lay the Dagorlad or the Battle Plain."""

from distutils.core import setup

setup(
    name="mordor",
    version="1.1",
    description="Land of Shadow",
    long_description=__doc__,
    author="Lukasz Langa",
    author_email="lukasz@langa.pl",
    url="http://pypi.python.org/pypi/mordor/",
    license="MIT",
    py_modules = ['mordor', 'ordor'],
    package_dir = {'': 'src'},
    platforms="Any",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Other Audience",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.1",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
    ],
)
