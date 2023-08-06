from distutils.core import setup

setup(
    name='Bla',
    version='0.1.0',
    author='Blabla',
    author_email='jrh@example.com',
    packages=None,
    scripts=None,
    url='http://pypi.python.org/pypi/Bla/',
    license='LICENSE.txt',
    description='Python source viewer.',
    long_description=open('README.rst').read(),
    install_requires=[
        "pygments >= 1.5",
    ],
)
