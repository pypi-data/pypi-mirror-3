import utils
import os
import logging

module_logger = logging.getLogger('localBFF.libLocalBFF.PayloadFile')

def getPayloadFilesFromMetafileDict(metafileDict):
  files = []
  payloadDirectory = metafileDict['info']['name'].decode('utf-8')
  
  if utils.isSingleFileMetafile(metafileDict):
    module_logger.debug('Metafile is in single-file mode')

    filename = payloadDirectory
    size = metafileDict['info']['length']
    streamOffset = 0
    
    files.append( PayloadFile(path="", filename=filename, size=size, streamOffset=streamOffset) )
  
  else:
    module_logger.debug('Metafile is in multi-file mode')
    
    numberOfFiles = len(metafileDict['info']['files'])
    module_logger.debug('Total files: ' + str(numberOfFiles))
    
    currentStreamOffset = 0
    for i in range(0, numberOfFiles):
      currentFile = metafileDict['info']['files'][i]
      path = os.path.join(payloadDirectory, *currentFile['path'][:-1])
      filename = currentFile['path'][-1].decode('utf-8')
      size = currentFile['length']
      index = i
      streamOffset = currentStreamOffset
      
      files.append( PayloadFile(path=path, filename=filename, size=size, streamOffset=streamOffset) )
      
      currentStreamOffset += size
  
  return files

class PayloadFile:
  def __init__(self, path, filename, size, streamOffset):
    self.path = path
    self.filename = filename
    self.size = size
    self.streamOffset = streamOffset
    self.endingOffset = streamOffset+size
    self.matchedFilePath = None
    self.status = "NOT_CHECKED"

    self.logger = logging.getLogger('localBFF.libLocalBFF.PayloadFile.PayloadFile')
    self.logger.debug(self)
  
  def __repr__(self):
    return self.__str__()

  def __str__(self):
    output = self.getPathFromMetafile() + "\n"
    output += "  Size: " + str(self.size) + "B\n"
    output += "  Payload substream: (" + str(self.streamOffset) + "B, " + str(self.endingOffset) + "B)\n"
    output += "  Status: " + self.status
    if self.matchedFilePath:
      output += "\n  Matched file: " + self.matchedFilePath
    return output
 
  def contributesTo(self, piece):   
    fileEndingOffset = self.streamOffset + self.size
    pieceEndingOffset = piece.streamOffset + piece.size
    
    pieceIsWholelyContainedInFile = ( self.streamOffset <= piece.streamOffset and fileEndingOffset >= pieceEndingOffset )

    fileBeginsBeforePieceBegins = self.streamOffset <= piece.streamOffset
    fileEndsAfterPieceBegins = fileEndingOffset > piece.streamOffset
    
    fileBeginsInsidePiece = self.streamOffset < pieceEndingOffset
    fileEndsAfterPieceEnds = fileEndingOffset > pieceEndingOffset
    
    fileIsPartiallyContainedInPiece = (fileBeginsBeforePieceBegins and fileEndsAfterPieceBegins) or (fileBeginsInsidePiece and fileEndsAfterPieceEnds)
    
    
    fileBeginsAfterPieceBegins = self.streamOffset >= piece.streamOffset
    fileEndsBeforePieceEnds = fileEndingOffset <= pieceEndingOffset
    
    fileIsWholelyContainedInPiece = fileBeginsAfterPieceBegins and fileEndsBeforePieceEnds
    return pieceIsWholelyContainedInFile or fileIsWholelyContainedInPiece or fileIsPartiallyContainedInPiece
  
  def hasNotBeenMatched(self):
    return not bool( self.matchedFilePath )
  
  def getPathFromMetafile(self):
    return os.path.join(self.path, self.filename)
  
  def getMatchedPathFromContentDirectory(self):
    return self.matchedFilePath
