from distutils.core import setup
import pollster

setup(
    name='Pollster',
    version=pollster.__version__,
    packages=['pollster',],
    license='BSD',
    author='Aaron Bycoffe',
    author_email='bycoffe@huffingtonpost.com',
    description="A Python wrapper for the Pollster API",
    long_description="A Python wrapper for the Pollster API",
    url='https://github.com/huffingtonpost/python-pollster',
    classifiers=[
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: BSD License',
                 'Natural Language :: English',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python',
                 'Topic :: Software Development :: Libraries :: Python Modules',
                 ],

)
