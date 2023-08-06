from distutils.core import setup

files = ["*"]

setup(
    name='Minidetector',
    version='0.1',
    packages=['minidetector',],
    license='BSD License',
    package_data = {'minidetector' : files },
    long_description=open('README.txt').read(),
)
