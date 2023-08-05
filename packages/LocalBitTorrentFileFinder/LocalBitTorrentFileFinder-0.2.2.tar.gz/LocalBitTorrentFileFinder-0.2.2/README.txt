LocalBFF: the Local BitTorrent File Finder
==========================================

Sometimes you rename files, or change the directory structure. Then, after a while, you go back to your BitTorrent client to have it all red! It can't find the files to seed them!

What do you do now? Well, if you believe "Sharing is Caring", you'll reseed those buggers soon.

Local BitTorent File Finder (**localbff**) is a command-line program intended to assist you in locating those lost files.

How to Use LocalBFF
-------------------

From the command line, call::

  $ localbff /path/to/torrentFile.torrent /path/to/directory/you/suspect/files/to/be/stored/in/

Simply give it the directory where the files could be, and a .torrent file of interest. It'll tell you if it finds the files, and where they are located!

What LocalBFF won't do
----------------------

It won't rename your files, and won't set them up for immediate re-seeding. lbff only provides you with the information for finding files that can be reseeded.

If you're interested in minimizing the amount of effort that is required to reseed your previously lost files, check out Allogamy for a GUI application or Putlog for a command line application.
