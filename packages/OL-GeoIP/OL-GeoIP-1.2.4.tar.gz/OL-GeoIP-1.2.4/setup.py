from setuptools import setup, Extension

description = """
This is a fork of the Maxmind GeoIP Python wrapper library originally from GitHub at 
https://github.com/jlopez/maxmind-geoip with some minor changes for the openlibrary.org project
"""

module1 = Extension('GeoIP',
                    libraries = ['GeoIP'],
                    sources = ['py_GeoIP.c'],
                    library_dirs = ['/opt/local/lib', '/usr/local/lib'],
                    include_dirs = ['/opt/local/include', '/usr/local/include'])

setup (name = 'OL-GeoIP',
       version = '1.2.4',
       description = description,
       ext_modules = [module1],
       maintainer = "Noufal Ibrahim",
       # url = "https://github.com/nibrahim/maxmind-geoip/tarball/master",
       # # url = "https://github.com/nibrahim/maxmind-geoip",
       maintainer_email = "noufal@archive.org")
