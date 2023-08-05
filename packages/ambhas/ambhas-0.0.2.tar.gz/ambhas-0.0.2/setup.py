from distutils.core import setup
setup(
    name = "ambhas",
    packages = ["ambhas"],
    version = "0.0.2",
    description = "A library devloped under the project AMBHAS",
    author = "Sat Kumar Tomer",
    author_email = "satkumartomer@gmail.com",
    url = "http://ambhas.com/",
    download_url = "http://ambhas.com/tools/ambhas-0.0.2.tar.gz",
    keywords = ["ambhas", "hydrology", "statistics", "modelling"],
    classifiers = [
        "Programming Language :: Python",
        "Development Status :: 3 - Alpha",
        "Environment :: Other Environment",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering",
        ],
    long_description=open('README.txt').read(),
)

