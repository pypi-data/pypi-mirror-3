from setuptools import setup
setup(
    name='pytest-couchdbkit',
    get_version_from_hg=True,

    description='py.test extension for per-test couchdb databases using couchdbkit',
    long_description=open("README").read(),

    author='RonnyPfannschmidt',
    author_email='ronny.pfannschmidt@gmx.de',

    url='http://bitbucket.prg/RonnyPfannschmidt/pytest-couchdbkit',
    packages=[
        'pytest_couchdbkit',
    ],

    entry_points = {
        'pytest11': [
            'couchdbkit = pytest_couchdbkit'
        ]
    },

    install_requires=[
        'pytest',
        'couchdbkit',
    ],
    setup_requires=['hgdistver'],
)
