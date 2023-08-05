from distutils.core import setup

setup(
    name='cmdstyle',
    version='0.1.0',
    py_modules=['cmdstyle'],
    author='Henri Wiechers',
    author_email='hwiechers@gmail.com',
    url='http://pypy.python.org/pypi/cmdstyle/',
    license='LICENSE.txt',
    description='Command line interface framework',
    long_description=open('README.txt').read(),
    keywords=["cli"],
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: User Interfaces"
        ]
)
