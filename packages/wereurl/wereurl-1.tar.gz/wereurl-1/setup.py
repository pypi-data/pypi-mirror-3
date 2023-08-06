from setuptools import setup

setup(
    name='wereurl',
    version='1',
    url='http://github.com/nickgartmann/wereurl/',
    license='BSD',
    author='Nick Gartmann',
    author_email='nick@rokkincat.com',
    description='A module for detecting links in blobs of text.',
    py_modules=['wereurl'],
    zip_safe=True,
    platforms='any',
    install_requires=[],
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
