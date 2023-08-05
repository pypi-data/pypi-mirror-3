from setuptools import setup, find_packages


setup(name='flask-geokit',
      version='0.1.5',
      packages=find_packages(),
      author='Alex Toney',
      author_email='toneyalex@gmail.com',
      url='',
      license='BSD',
      include_package_data=True,
      description='Geocoding toolkit',
      zip_safe=False,
      long_description='',
      platforms=['any'],
      classifiers='',
      install_requires=['furl', 'geohash', 'Flask>=0.3'],
)
