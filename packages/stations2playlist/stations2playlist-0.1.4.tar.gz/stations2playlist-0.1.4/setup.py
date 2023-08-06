from distutils.core import setup

setup(name = 'stations2playlist',
      version = '0.1.4',
      author = 'Costin Stroie',
      author_email = 'costinstroie@eridu.eu.org',
      scripts = ['stations2playlist.py'],
      url = 'http://pypi.python.org/pypi/stations2playlist/',
      license = 'GPL',
      description = 'Create a playlist with all stations of a radio such as SKY.FM or Digitally Imported',
      long_description = open('README', 'rb').read(),
      classifiers = ['Development Status :: 4 - Beta',
                     'Environment :: Console',
                     'Intended Audience :: End Users/Desktop',
                     'License :: OSI Approved :: GNU General Public License (GPL)',
                     'Operating System :: OS Independent',
                     'Programming Language :: Python',
                     'Programming Language :: Python :: 2',
                     'Programming Language :: Python :: 2.6',
                     'Topic :: Multimedia :: Sound/Audio']
)
# vim: set ft=python ai ts=4 sts=4 et sw=4 sta nowrap nu :
