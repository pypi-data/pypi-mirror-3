"""
Setup script for PyTeVCat
$Id: setup.py 12 2012-01-04 04:07:09Z oxon $
"""

from numpy.distutils.core import setup

setup(name="PyTeVCat",
      version="1.1.2",
      description="Python wrapper for TeVCat",
      author="Akira Okumura",
      author_email="oxon@mac.com",
      url='https://sourceforge.net/p/pytevcat/',
      license='BSD License',
      platforms=['MacOS :: MacOS X', 'POSIX', 'Windows'],
      packages=["tevcat"],
      install_requires=['astropysics', 'networkx'],
      package_data={"tevcat": ["img/*.png",]},
      classifiers=['Topic :: Scientific/Engineering :: Astronomy',
                   'Topic :: Scientific/Engineering :: Physics',
                   'Development Status :: 4 - Beta',
                   'Programming Language :: Python',
                   ],
      long_description='tevcat.Python interface for TeVCat (http://tevcat.uchicago.edu/)'
      )
