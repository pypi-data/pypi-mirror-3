import os
from setuptools import setup, find_packages

version = '0.2.3b'
README = os.path.join(os.path.dirname(__file__), 'README.rst')
long_description = open(README).read() + 'nn'

setup(
      name='ComplexSystems',
      packages=find_packages(),
      version=version,
      description='Toolbox for Complex Sytems including : Human Based Mobility Models',
      long_description=long_description,
      author='Vincent Gauthier',
      author_email='vgauthier@luxbulb.org',
      url='http://bitbucket.org/vgauthier/complex-systemes/',
      keywords=["complex systems", "Levy flight", "human mobility"],
      requires=['numpy',' scikits','pylab'],
      license='MIT',
      tests_require=['nose'],
      test_suite = 'nose.collector',
      platforms=['any'],
      classifiers=[
                   'License :: OSI Approved :: MIT License',
                   'Programming Language :: Python',
                   'Programming Language :: Python :: 2.7',
                   'Operating System :: OS Independent',
                   'Topic :: Scientific/Engineering :: Mathematics',
                   'Development Status :: 4 - Beta',
                   'Intended Audience :: Science/Research'
                   ],
      install_requires=[
                        "numpy >= 1.6.0"
                        ]
      )
