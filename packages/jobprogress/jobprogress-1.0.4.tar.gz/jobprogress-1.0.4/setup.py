from setuptools import setup

CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Programming Language :: Python :: 3',
]

LONG_DESC = open('README', 'rt').read() + '\n\n' + open('CHANGES', 'rt').read()

setup(
    name='jobprogress',
    version='1.0.4',
    author='Hardcoded Software',
    author_email='hsoft@hardcoded.net',
    packages=['jobprogress'],
    scripts=[],
    url='http://hg.hardcoded.net/jobprogress/',
    license='BSD License',
    description='Cross-toolkit UI progress tracking',
    long_description=LONG_DESC,
    classifiers=CLASSIFIERS,
)