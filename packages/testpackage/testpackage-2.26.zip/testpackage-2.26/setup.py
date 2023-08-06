from setuptools import setup, find_packages

version = '2.26'

setup(name='testpackage',
      version=version,
      description='Test package.',
      long_description=open('README.txt').read(),
      classifiers=[
          'Programming Language :: Python',
      ],
      keywords='test package',
      author='Jarn AS',
      author_email='info@jarn.com',
      url='http://www.jarn.com/',
      license='private',
      packages = ['testpackage'],
      zip_safe=False,
      install_requires=[
          'setuptools',
      ],
)
