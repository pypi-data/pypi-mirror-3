
import os
from setuptools import setup, find_packages

import gstudio

setup(name='gnowsys-studio',
      version=gstudio.__version__,

      description='A collaborative blogspace for constructing and publishing semantic knowledge networks and ontologies',
      long_description='\n'.join([open('README.rst').read(),
                                  open(os.path.join('docs', 'install.rst')).read(),
                                  open(os.path.join('docs', 'changelog.rst')).read(),]),
      keywords='django, blog, post, news, gnowsys, gnowledge, semantic, networks, ontolgies, concept map, concept graph',

      author=gstudio.__author__,
      author_email=gstudio.__email__,
      url=gstudio.__url__,

      packages=find_packages(exclude=['demo','demo.graphviz','demo.graphviz.management','demo.graphviz.management.commands']),
      
      classifiers=[
          'Framework :: Django',
          'Development Status :: 3 - Alpha',
          'Environment :: Web Environment',
          'Programming Language :: Python',
          'Intended Audience :: Developers',
          'Operating System :: OS Independent',
          'License :: OSI Approved :: GNU Affero General Public License v3',
          'Topic :: Scientific/Engineering :: Artificial Intelligence',
          'Topic :: Scientific/Engineering :: Information Analysis',
          'Topic :: Scientific/Engineering :: Visualization',],




      license=gstudio.__license__,
      include_package_data=True,
      zip_safe=False,
      install_requires=['BeautifulSoup>=3.2.0',
                        'django-mptt>=0.4.2',
                        'django-tagging>=0.3.1',
                        'django-xmlrpc>=0.1.3',
                        'pyparsing>=1.5.5',
                        'django-reversion>=1.5.1',
                        'django-grappelli>=2.3.4',
                        'django-ratings>=0.3.6',
                        'rdflib>=3.0.0',
                        'django-registration>=0.8',


                        ])
