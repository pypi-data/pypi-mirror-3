import os
from setuptools import setup, find_packages


version = '1.0'


def read_file(name):
    name = name.split('/')
    return open(os.path.join(os.path.dirname(__file__), *name)).read()


docs = []
docs.append(read_file('README.rst'))


setup(name='cykooz.djangopaste',
      version=version,
      description='A wrapper that allows us to run Django under PasteDeploy',
      long_description='\n\n'.join(docs),
      classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        'Framework :: Django',
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      keywords='web application server wsgi django',
      author='Cykooz',
      author_email='saikuz@mail.ru',
      url='https://bitbucket.org/cykooz/cykooz.djangopaste',
      license='BSD-derived',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['cykooz', ],
      include_package_data=True,
      zip_safe=False,
      extras_require={
            'test': []
            },
      install_requires=[
            'distribute',
            'Django',
            'PasteScript'
            ],
      entry_points = '''
        [paste.app_factory]
        django = cykooz.djangopaste:make_django
      '''
      )

