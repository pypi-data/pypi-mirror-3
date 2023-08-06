from distutils.core import setup

setup(
    name='SLOTH',
    version='0.0.8',
    author='M.Kauer',
    author_email='kauer@mpi-cbg.de',
    packages=['sloth', 'sloth.test'],
    scripts=['bin/image_analyser.py', 'bin/select_ROI.py','bin/automatic_analysis1.0.py', 'bin/sloth-main.py', 'Sloth3.gif'],
    url='http://pypi.python.org/pypi/Sloth/',
    license='LICENSE.txt',
    description='stick-like object tracker',
    long_description=open('README.txt').read(),
    install_requires=[
        "matplotlib >= 0.99.3",
        "numpy  >= 1.5.1",
	"scipy  >= 0.8.0"
    ]
)
