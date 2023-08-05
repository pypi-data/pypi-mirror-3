from setuptools import setup, find_packages

setup(
    name="psycogreen",
    version="0.0.1",
    author="Daniele Varrazzo",
    packages=find_packages(),
    install_requires=[
        'psycopg2',
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
    ],
)
