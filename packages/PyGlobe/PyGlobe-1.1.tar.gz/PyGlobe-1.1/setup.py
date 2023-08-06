import pyglobe


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='PyGlobe',
    version=pyglobe.__version__,
    description='Python interface for Globe Labs API',
    author='Ferdinand Silva',
    author_email='ferdinandsilva@ferdinandsilva.com',
    packages=['pyglobe'],
    install_requires=['suds'],
    url='http://ferdinandsilva.com',
    classifiers=(
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python',
        'License :: Freeware',
    ),
    download_url='https://github.com/six519/PyGlobe',
)
