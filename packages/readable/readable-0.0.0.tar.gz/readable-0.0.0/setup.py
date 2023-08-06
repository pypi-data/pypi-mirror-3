from setuptools import setup, find_packages

requires = ['WebError','mock', 'webtest', 'BeautifulSoup']

setup(name='readable',
      version='0.0.0',
      description='testing and assertion library',
      long_description='',
      classifiers=[
        "Programming Language :: Python",
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        ],
      author='Jasper van den Bosch',
      author_email='jasper@ilogue.com',
      url='http://ilogue.com',
      keywords='',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      test_suite="ilogue.readable.tests",
      )

