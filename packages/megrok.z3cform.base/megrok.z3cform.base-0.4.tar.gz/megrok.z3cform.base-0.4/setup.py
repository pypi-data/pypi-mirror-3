from os.path import join
from setuptools import setup, find_packages

name = 'megrok.z3cform.base'
version = '0.4'
readme = open(join('src', 'megrok', 'z3cform', 'base', 'README.txt')).read()
history = open(join('docs', 'HISTORY.txt')).read()

install_requires = [
    'setuptools',
    'grokcore.component',
    'grokcore.viewlet',
    'grokcore.view',
    'grokcore.formlib',
    'z3c.form >= 2.1',
    'megrok.layout >= 0.9',
    'megrok.pagetemplate >= 0.3',
    'rwproperty',
    ]

test_requires = install_requires + ['grok >= 1.0', 'zope.app.testing']

setup(name=name,
      version=version,
      description="megrok extension for z3cform",
      long_description = readme + '\n\n' + history,
      keywords='Grok Form',
      author='Souheil Chelfouh',
      author_email='trollfot@gmail.com',
      url='',
      license='ZPL 2.1',
      packages=find_packages('src', exclude=['ez_setup']),
      package_dir={'': 'src'},
      namespace_packages=['megrok', 'megrok.z3cform'],
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      extras_require={'test': test_requires,},
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: Zope Public License",
        ],
      )
