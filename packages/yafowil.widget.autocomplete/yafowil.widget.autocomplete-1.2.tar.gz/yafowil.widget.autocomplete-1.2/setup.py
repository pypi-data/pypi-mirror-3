from setuptools import setup, find_packages
import sys, os

version = '1.2'
shortdesc = 'Autocomplete Widget for YAFOWIL - Yet Another Form Widget Library (Python, Web)'
longdesc = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()
longdesc += open(os.path.join(os.path.dirname(__file__), 'HISTORY.rst')).read()
longdesc += open(os.path.join(os.path.dirname(__file__), 'LICENSE.rst')).read()
tests_require = ['yafowil[test]', 'yafowil.webob', 'gunicorn', 'simplejson']

setup(name='yafowil.widget.autocomplete',
      version=version,
      description=shortdesc,
      long_description=longdesc,
      classifiers=[
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Topic :: Software Development',
            'Topic :: Internet :: WWW/HTTP :: Dynamic Content', 
            'License :: OSI Approved :: BSD License',            
      ],
      keywords='jquery jquery.ui.autocomplete widget yafowil',
      author='BlueDynamics Alliance',
      author_email='dev@bluedynamics.com',
      url=u'http://pypi.python.org/pypi/yafowil.widget.autocomplete',
      license='Simplified BSD',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['yafowil', 'yafowil.widget'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'yafowil',
      ],
      tests_require=tests_require,
      test_suite="yafowil.widget.autocomplete.tests.test_suite",
      extras_require = dict(
          test=tests_require,
      ),
      entry_points="""
      # plone specific, ignore if not available
      [z3c.autoinclude.plugin]
      target = plone
      """,       
      
      )
