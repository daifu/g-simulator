from setuptools import setup, find_packages
setup(
    name = "pygnutella",
    version = "1.0",
    packages = find_packages(exclude=["tests", "examples"]),

    # installed or upgraded on the target machine
    # other packages are asyncore, asynchat, multiprocessing, uuid, struct, socket 
    # are Python standard libraries
    # http://docs.python.org/library/
    install_requires = ['numpy'],

    # metadata for upload to PyPI
    author = "Khai Nguyen, Daifu Ye, Tai Pham",
    author_email = "khaing211@gmail.com, daifu.ye@gmail.com, taiducpham@ucla.edu",
    description = "This is Gnutella implementation on top of Python asyncore.",
    license = "MIT",
    keywords = "gnutella, python, asyncore, pygnutella, p2p, peer-to-peer, peer network",
)
