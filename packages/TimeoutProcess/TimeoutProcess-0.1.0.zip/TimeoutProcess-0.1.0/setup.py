from distutils.core import setup

setup(
    name='TimeoutProcess',
    version='0.1.0',
    author='Eugene Ching',
    author_email='eugene@enegue.com',
    packages=['timeoutprocess'],
    url='http://pypi.python.org/pypi/TimeoutProcess/',
    license='LICENSE.txt',
    description='Run a process with a timeout attached to it.',
    long_description=open('README.txt').read(),
)

