from setuptools import setup, find_packages
from os.path import join

version = '1.0a4'
readme = open(join('README.txt')).read()
history = open(join('docs', 'HISTORY.txt')).read()

setup(name = 'collective.js.showmore',
      version = version,
      description = 'JS add-on to show/hide parts of a page.',
      long_description = readme[readme.find('\n\n'):] + '\n' + history,
      classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
      ],
      keywords = 'javascript ajax jquery expansion expand markup',
      author = 'Godefroid Chapelle',
      author_email = 'gotcha@jarn.com',
      url = 'http://pypi.python.org/pypi/collective.js.showmore/',
      license = 'GPL',
      packages = find_packages(exclude=['ez_setup']),
      namespace_packages = ['collective', 'collective.js'],
      include_package_data = True,
      platforms = 'Any',
      zip_safe = False,
      install_requires = [
          'setuptools',
      ],
      entry_points = '',
)
