from distutils.core import setup

setup(
    name='SlimES',
    version='0.0.1',
    author='Radu Gheorghe',
    author_email='radu0gheorghe@gmail.com',
    packages=['slimes'],
    url='http://pypi.python.org/pypi/SlimES/',
    license='LICENSE.txt',
    description='Thin Python connector for Elasticsearch.',
    long_description=open('README.txt').read(),
    install_requires=[
        "requests >= 0.8.2",
    ],
)
