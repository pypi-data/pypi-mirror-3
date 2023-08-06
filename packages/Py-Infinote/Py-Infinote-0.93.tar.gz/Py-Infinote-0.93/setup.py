import os
from setuptools import setup


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


setup(
    name='Py-Infinote',
    version="0.93",
    description="Py-Infinote is a Python implementation of the infinote \
    operation transformation protocol. It's a direct port of JInfinote",
    long_description=(read('README.rst')),
    author="Jeroen van Veen",
    author_email="j.veenvan@gmail.com",
    url="https://github.com/phrearch/py-infinote",
    license="BSD",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Information Technology",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Topic :: Software Development",
        "Operating System :: OS Independent"
    ],
    packages=('infinote', ),
    keywords="infinote,text,editing,collaborative,ot,adopted",
    include_package_data=True,
    zip_safe=False,
)
