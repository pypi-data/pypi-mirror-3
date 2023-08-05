from setuptools import setup

long_description = (
    open('README.txt').read()
    + '\n' +
    open('CHANGES.txt').read())

setup(
    name='jslex',
    version='0.1',
    description="JsLex makes JavaScript more edible by xgettext (in C mode).",
    classifiers=[],
    keywords='',
    author='Ned Batchelder',
    long_description=long_description,
    license='BSD',
    url='https://bitbucket.org/ned/jslex',
    py_modules=['jslex'],
    zip_safe=False,
    )
