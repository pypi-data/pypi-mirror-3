from distutils.core import setup

setup(
      name='ComplexSystems',
      packages=['complex_systems', 'complex_systems.mobility'],
      version='0.1.1',
      description='Toolbox for Complex Sytems including : Human Based Mobility Models',
      author='Vincent Gauthier',
      author_email='vgauthier@luxbulb.org',
      url='http://www-public.it-sudparis.eu/~gauthier/',
      requires=['numpy', 'matplotlib'],
      license='MIT',
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
