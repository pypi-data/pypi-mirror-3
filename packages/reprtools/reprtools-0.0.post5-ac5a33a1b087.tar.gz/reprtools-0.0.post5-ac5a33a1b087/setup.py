from setuptools import setup
from os.path import abspath, dirname, join
readme = join(dirname(abspath(__file__)), 'README')
if __name__=='__main__':
    setup(
        name='reprtools',
        author="Ronny Pfannschmidt",
        author_email="Ronny.Pfannschmidt@gmx.de",
        description="utilities for nice object reprs",
        long_description=open(readme).read(),
        py_modules=[
            'reprtools',
        ],
        get_version_from_hg=True,
        setup_requires=[
            'hgdistver',
        ],
    )
