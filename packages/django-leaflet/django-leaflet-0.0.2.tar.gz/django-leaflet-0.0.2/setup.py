import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

setup(
    name='django-leaflet',
    version='0.0.2',
    author='Mathieu Leplatre',
    author_email='mathieu.leplatre@makina-corpus.com',
    url='https://github.com/makinacorpus/django-leaflet',
    download_url = "http://pypi.python.org/pypi/django-leaflet/",
    description="Use Leaflet in your django projects",
    long_description=open(os.path.join(here, 'README.rst')).read(),
    install_requires=[],
    packages=find_packages(),
    include_package_data = True,
    zip_safe = False,
    classifiers  = ['Topic :: Utilities', 
                    'Natural Language :: English',
                    'Operating System :: OS Independent',
                    'Intended Audience :: Developers',
                    'Environment :: Web Environment',
                    'Framework :: Django',
                    'Development Status :: 5 - Production/Stable',
                    'Programming Language :: Python :: 2.7'],
)
