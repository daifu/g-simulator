from setuptools import setup, find_packages
setup(
    name = "pygnutella",
    version = "1.0",
    packages = find_packages(exclude=["tests", "examples"]),

    # installed or upgraded on the target machine
    install_requires = ['asyncore', 
                        'asynchat',
                        'multiprocessing', 
                        'uuid', 
                        'numpy',
                        'logging',
                        'struct',
                        'socket'],

    # metadata for upload to PyPI
    author = "Khai Nguyen, Daifu Ye, Tai Pham",
    author_email = "khaing211@gmail.com, daifu.ye@gmail.com, taiducpham@ucla.edu",
    description = "This is Gnutella implementation on top of Python asyncore.",
    license = "MIT",
    keywords = "gnutella, python, asyncore, pygnutella, p2p, peer-to-peer, peer network",
)