from setuptools import setup, find_packages


CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: Zope Public License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
]

desc = open('README.txt').read().strip()
changes = open('CHANGES.txt').read().strip()
long_description = desc + '\n\nChanges\n=======\n\n'  + changes

setup(
    name='pypimirror',
    version = '1.0.16.4',
    author='Daniel Kraft, Andreas Jung et al.',
    author_email='dk@d9t.de',
    description='A module for building a complete or a partial PyPI mirror',
    long_description=long_description,
    maintainer='Andreas Jung',
    maintainer_email='lists@zopyx.com',
    classifiers=CLASSIFIERS,
    package_dir = {'': 'src'},
    packages=find_packages('src'),
    include_package_data=True,
    package_data={
        '' : ['*.txt', '*.sample'],
    },
    zip_safe=False,
    install_requires = ['setuptools',
                        'zc.lockfile',
                        'BeautifulSoup'],
    extras_require = {
        'test': [ 'zc.buildout',  
                  'zope.testing',
                  'interlude' ],
    },
    entry_points = dict(console_scripts=[
        'pypimirror = pypimirror.mirror:run',
        ])
    )
