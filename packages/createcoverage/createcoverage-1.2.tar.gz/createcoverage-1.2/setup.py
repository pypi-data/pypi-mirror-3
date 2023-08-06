from setuptools import setup

version = '1.2'

long_description = '\n\n'.join([
    open('README.txt').read(),
    open('TODO.txt').read(),
    open('CREDITS.txt').read(),
    open('CHANGES.txt').read(),
    ])

install_requires = [
    'setuptools',
    'coverage >= 3.4',
    ],

tests_require = [
    ]

setup(name='createcoverage',
      version=version,
      description="Single command to create coverage reports (assumes a bin/test)",
      long_description=long_description,
      # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[],
      keywords=[],
      author='Reinout van Rees',
      author_email='reinout@vanrees.org',
      url='',
      license='GPL',
      packages=['createcoverage'],
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      tests_require=tests_require,
      extras_require = {'test': tests_require},
      entry_points={
          'console_scripts': [
              'createcoverage = createcoverage.script:main',
              # Hack to make sure bin/coverage exists when we don't otherwise
              # explicitly tell buildout to create the script for this.
              'coverage = coverage:main',
          ]},
      )
