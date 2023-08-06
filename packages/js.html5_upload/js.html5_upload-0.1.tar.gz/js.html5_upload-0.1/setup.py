from setuptools import setup, find_packages
import os

version = '0.1'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (read('README.txt')
                    + '\n' +
                    read('CHANGES.txt'))

setup(name='js.html5_upload',
      version=version,
      description="Fanstatic packaging of jquery-html5-upload",
      long_description=long_description,
      classifiers=[],
      keywords='',
      #author='podhmo podhmo',
      #author_email='podhmo@example.jp',
      #url="https://github.com/podhmo/js.backbone",
      #license='BSD',
      packages=find_packages(),
      namespace_packages=['js'],
      include_package_data=True,
      zip_safe=False,
      #setup_requires=['hgtools'],
      install_requires=['fanstatic',
                        'setuptools',
                        'js.jquery'],
      entry_points={'fanstatic.libraries': ['main = js.html5_upload:library',],},)
