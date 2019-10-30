import io
import re
from setuptools import setup, find_packages


with io.open("README.rst", "rt", encoding="utf-8") as f:
    readme = f.read()

setup(
    name="py-compile-wrapper",
    version="1.0.0.dev",
    long_description=readme,
    author="Nguyen Khac Thanh",
    author_email="nguyenkhacthanh244@gmail.com",
    url="https://github.com/nkthanh98/py-compile-wrapper",
    packages=find_packages("src/py_compile_wrapper", exclude=["test*", "examples"]),
    license="MIT",
    python_requires=">=3.5",
    test_suite="tests",
    entry_points = {
        'console_scripts': [
            'pyc = src.py_compile_wrapper:run',
        ],
    }
)
