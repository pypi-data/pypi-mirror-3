from setuptools import setup, find_packages

version = '0.1.5'

setup(name='hadrian',
      version=version,
      description="A Collection of Django packages and scripts",
      long_description=open("README.md", "r").read(),
      classifiers=[
          "Development Status :: 3 - Alpha",
          "Environment :: Web Environment",
          "Intended Audience :: End Users/Desktop",
          "Natural Language :: English",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
          "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries",
          "Topic :: Utilities",
          "License :: OSI Approved :: MIT License",
          ],
      keywords='',
      author='Derek Stegelman',
      author_email='dstegelman@gmail.com',
      url='http://github.com/dstegelman/hadrian',
      license='MIT',
      packages=find_packages(),
      install_requires = ['fabric',],
      include_package_data=True,
      zip_safe=False,
    )
