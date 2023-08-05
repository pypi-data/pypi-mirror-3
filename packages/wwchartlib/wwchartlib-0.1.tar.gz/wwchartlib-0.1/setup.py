from distutils.core import setup

with open('README') as file:
    long_description = file.read()

setup(
    name='wwchartlib',
    version='0.1',
    description='Collection of Qt chart widgets',
    author='Fraser Tweedale',
    author_email='frasert@jumbolotteries.com',
    url='https://gitorious.org/wwchartlib',
    packages=['wwchartlib', 'wwchartlib.test'],
    data_files=[
        (
            'doc/wwchartlib/examples',
            ['examples/piechart.py', 'examples/adjustablepiechart.py']
        ),
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: X11 Applications :: Qt',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: '
            'GNU Library or Lesser General Public License (LGPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Widget Sets',
    ],
    long_description=long_description,
)
