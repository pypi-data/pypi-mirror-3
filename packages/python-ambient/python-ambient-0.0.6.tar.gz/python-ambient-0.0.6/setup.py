from setuptools import setup, find_packages

setup(
    name='python-ambient',
    version='0.0.6',
    description='Python Ambient Mobile integration library.',
    long_description = open('README.rst', 'r').read() + open('AUTHORS.rst', 'r').read() + open('CHANGELOG.rst', 'r').read(),
    author='Praekelt Foundation',
    author_email='dev@praekelt.com',
    license='BSD',
    url='http://github.com/praekelt/python-ambient',
    packages = find_packages(),
    include_package_data=True,
    classifiers = [
        "Programming Language :: Python",
        "License :: OSI Approved :: BSD License",
        "Development Status :: 4 - Beta",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
    ],
    zip_safe=False,
)
