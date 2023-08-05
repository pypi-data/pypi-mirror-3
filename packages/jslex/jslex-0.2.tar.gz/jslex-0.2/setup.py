from setuptools import setup

long_description = (
    open('README.txt').read()
    + '\n' +
    open('CHANGES.txt').read())

setup(
    name='jslex',
    version='0.2',
    description="JsLex makes JavaScript more edible by xgettext (in C mode).",
    classifiers=[],
    keywords='',
    author='Ned Batchelder',
    long_description=long_description,
    license='BSD',
    url='https://bitbucket.org/ned/jslex',
    py_modules=['jslex', 'jslex_scripts'],
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'jslex_prepare = jslex_scripts:jslex_prepare'
            ]
        }
    )
