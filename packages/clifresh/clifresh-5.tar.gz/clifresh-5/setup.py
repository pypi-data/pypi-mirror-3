from setuptools import setup

setup(
    name='clifresh',
    version='5',
    url='http://github.com/nickgartmann/clifresh/',
    license='BSD',
    author='Nick Gartmann',
    author_email='nick@rokkincat.com',
    description='A tool for logging time in '
                'the freshbooks invoice service.',
    py_modules=['clifresh'],
    zip_safe=True,
    platforms='any',
    install_requires=[
        'argparse',
        'refreshbooks'
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    entry_points={
        "console_scripts":set([
            "clifresh = clifresh:main"
        ])
    }
)
