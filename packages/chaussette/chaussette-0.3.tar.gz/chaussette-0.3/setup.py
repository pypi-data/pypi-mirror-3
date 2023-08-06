from setuptools import setup, find_packages


install_requires = []


with open('README.rst') as f:
    README = f.read()


setup(name='chaussette',
      version='0.3',
      url='http://chaussette.readthedocs.org',
      packages=find_packages(),
      description=("A WSGI Server for Circus"),
      long_description=README,
      author="Tarek Ziade",
      author_email="tarek@ziade.org",
      include_package_data=True,
      zip_safe=False,
      classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: Apache Software License",
        "Development Status :: 1 - Planning"],
      install_requires=install_requires,
      test_requires=['nose'],
      test_suite='nose.collector',
      entry_points="""
      [console_scripts]
      chaussette = chaussette.server:main
      """)
