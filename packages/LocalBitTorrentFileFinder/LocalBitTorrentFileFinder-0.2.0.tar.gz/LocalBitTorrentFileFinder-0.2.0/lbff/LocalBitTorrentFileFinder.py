import BitTorrentMetafile
import ContentDirectoryDao
import logging

class LocalBitTorrentFileFinder:
  def __init__(self, metafilePath=None, contentDirectory=None):
    self.metafilePath = metafilePath
    self.contentDirectory = contentDirectory
    self.logger = logging.getLogger('localBFF.libLocalBFF.LocalBitTorrentFileFinder')
    
    self.metafile = None
    self.dao = None
    self.files = None
  
  def processMetafile(self):
    self.logger.info("Stage 1: Processing metainfo file...")
    self.metafile = BitTorrentMetafile.getMetafileFromPath(self.metafilePath)
    
    self.logger.debug("Number of Files: " + str(self.metafile.numberOfFiles))
    self.logger.debug("Payload size: " + str(self.metafile.payloadSize))
    self.logger.debug("Number of Pieces: " + str(self.metafile.numberOfPieces))
    self.logger.debug("Piece size: " + str(self.metafile.pieceSize))
    self.logger.debug("Final piece size: " + str(self.metafile.finalPieceSize))
    
    self.logger.debug("File descriptions:")
    for f in self.metafile.files:
      self.logger.debug("Path: "+ f.getPathFromMetafile())
      self.logger.debug("Size: "+ str(f.size))
  
  def gatherAllFilesFromContentDirectory(self):
    self.logger.info("Stage 2: Walking content directory...")
    self.dao = ContentDirectoryDao.getAllFilesInContentDirectory(self.contentDirectory)
 
  def connectFilesInMetafileToPossibleMatchesInContentDirectory(self):
    self.logger.info("Stage 3: Finding all file system files that match by size...")
    if self.dao == None:
      self.gatherAllFilesFromContentDirectory()
    
    self.files = self.metafile.files
    
    for payloadFile in self.files:
      self.logger.debug("Current file:")
      self.logger.debug(payloadFile)
      payloadFile.possibleMatches = self.dao.getAllFilesOfSize( payloadFile.size )
      self.logger.debug("Possible matches: " + str(len(payloadFile.possibleMatches)))
      
  
  def positivelyMatchFilesInMetafileToPossibleMatches(self):
    self.logger.info("Stage 4: Matching files in the file system to files in metafile...")
    for piece in self.metafile.pieces:
      piece.findMatch()
