from distutils.core import setup

with open('README.txt') as f:
    long_description = f.read()

setup(
    name='weirdict',
    version='0.1.0',
    author='Baptiste Mispelon',
    author_email='bmispelon@gmail.com',
    packages=['weirdict'],
    url='https://github.com/bmispelon/weirdict',
    license='LICENSE.txt',
    description='Doing weird things with dicts.',
    long_description=long_description,
)
