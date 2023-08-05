from setuptools import setup, find_packages
from os.path import join

version = open(join('Products', 'ImageRepository', 'version.txt')).read().strip()
readme = open("README.txt").read()
history = open(join('docs', 'HISTORY.txt')).read()

setup(name = 'Products.ImageRepository',
      version = version,
      description = 'A centralized image repository with keyword/tag-based browsing and filtering.',
      long_description = readme[readme.find('\n\n'):] + '\n' + history,
      classifiers = [
        'Environment :: Web Environment',
        'Framework :: Plone',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
      ],
      keywords = 'plone images repository centralized keywords',
      author = 'Jarn AS',
      author_email = 'info@jarn.com',
      url = 'http://plone.org/products/imagerepository',
      license = 'GPL',
      packages = find_packages(exclude=['ez_setup']),
      namespace_packages = ['Products'],
      include_package_data = True,
      platforms = 'Any',
      zip_safe = False,
      install_requires = ['setuptools',],
)
