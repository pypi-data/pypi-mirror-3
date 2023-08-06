from setuptools import setup, find_packages


def read(name):
    return open(name).read()

name = 'erp5.extension.sectionextender'
version = '0.3.1'
long_description = (read('README.txt') + '\n'
                    )

setup(name=name,
      version=version,
      author='Arnaud Fontaine',
      author_email='arnaud.fontaine@nexedi.com',
      description='Buildout extension to extend only sections in parts',
      long_description=long_description,
      license="ZPL 2.1",
      keywords="buildout extension sections",
      classifiers=["License :: OSI Approved :: Zope Public License",
                     "Framework :: Buildout"],
      package_dir={'': 'src'},
      package_data={'': ['*.txt']},
      packages=find_packages('src'),
      namespace_packages=['erp5', 'erp5.extension'],
      include_package_data=True,
      url='https://github.com/Apkawa/erp5.extension.sectionextender',
      install_requires=['setuptools'],
      entry_points={'zc.buildout.extension':
                      ['ext = %s:ext' % name]},
      )
