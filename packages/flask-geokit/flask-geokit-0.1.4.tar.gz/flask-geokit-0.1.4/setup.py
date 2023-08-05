from setuptools import setup, find_packages


setup(name='flask-geokit',
      version='0.1.4',
      packages=find_packages(),
      author='Alex Toney',
      author_email='toneyalex@gmail.com',
      url='',
      license='BSD',
      include_package_data=True,
      description='Geocoding toolkit',
      long_description='',
      platforms=['any'],
      classifiers='',
      install_requires=['furl', 'geohash'],
)
