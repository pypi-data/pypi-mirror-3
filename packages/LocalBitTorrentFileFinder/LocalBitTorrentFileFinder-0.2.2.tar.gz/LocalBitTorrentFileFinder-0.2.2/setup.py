from distutils.core import setup

setup(
  name='LocalBitTorrentFileFinder',
  version='0.2.2',
  packages=['lbff',],
  scripts=['bin/localbff',],
  author='torik',
  author_email='vlad.marcenne@gmail.com',
  url='https://bitbucket.org/torik/local-bittorrent-file-finder/wiki/Home',
  license='Python Software Foundation License',
  description='Find local files described in a BitTorrent metafile',
  long_description=open('README.txt').read(),
  requires=[
    "argparse (>=1.2.1)",
    "bencode (==1.0)",
  ],
)
