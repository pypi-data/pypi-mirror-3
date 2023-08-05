import utils
import logging
import FileContributingToPiece
from AllContributingFilesToPiece import AllContributingFilesToPiece

module_logger = logging.getLogger('localBFF.libLocalBFF.PayloadPiece')

def getPiecesFromMetafileDict( metafileDict ):
  payloadSize = getPayloadSizeFromMetafileDict(metafileDict)
  module_logger.debug('Payload size: ' + str(payloadSize) + ' Bytes')
  
  hashes = getHashesFromMetafileDict(metafileDict)
  
  pieceSize = getPieceSizeFromDict(metafileDict)
  finalPieceSize = getFinalPieceSizeFromDict(metafileDict)

  pieces = []
  streamOffset = 0
  numberOfPieces = getNumberOfPiecesFromDict(metafileDict)

  module_logger.debug('Pieces: (' + str(numberOfPieces) + "x " + str(pieceSize) + "B) + " + str(finalPieceSize))
  
  for pieceIndex in range(numberOfPieces-1):
    pieces.append( PayloadPiece(size=pieceSize, hash=hashes[pieceIndex], streamOffset=streamOffset, index=pieceIndex+1) )
    streamOffset += pieceSize

  finalPiece = PayloadPiece(size=finalPieceSize, hash=hashes[-1], streamOffset=streamOffset, index=numberOfPieces)
  pieces.append(finalPiece)
  
  return pieces

def getPayloadSizeFromMetafileDict( metafileDict ):
  if utils.isSingleFileMetafile(metafileDict):
    return metafileDict['info']['length']
  
  else:
    payloadSize = 0
    for f in metafileDict['info']['files']:
        payloadSize += f['length']
    return payloadSize

def getHashesFromMetafileDict(metafileDict):
  concatenatedHashes = metafileDict['info']['pieces']
  return splitConcatenatedHashes(concatenatedHashes)

def splitConcatenatedHashes(concatenatedHashes):
  SHA1_HASH_LENGTH = 20
  return [concatenatedHashes[start:start+SHA1_HASH_LENGTH] for start in range(0, len(concatenatedHashes), SHA1_HASH_LENGTH)]

def getPieceSizeFromDict(metafileDict):
  return metafileDict['info']['piece length']

def getFinalPieceSizeFromDict(metafileDict):
  return getPayloadSizeFromMetafileDict(metafileDict) % getPieceSizeFromDict(metafileDict)

def getNumberOfPiecesFromDict(metafileDict):
  return len(getHashesFromMetafileDict(metafileDict))

class PayloadPiece:
  def __init__(self, size, streamOffset, hash, index):
    self.size = size
    self.streamOffset = streamOffset
    self.endingOffset = streamOffset+size
    self.hash = hash
    self.index = index
    self.contributingFiles = AllContributingFilesToPiece()

    self.logger = logging.getLogger('localBFF.libLocalBFF.PayloadPiece.PayloadPiece')
    self.logger.debug(self)
  
  def __repr__(self):
    return self.__str__()

  def __str__(self):
    output = "Piece #" + str(self.index) + ":(" + str(self.streamOffset) + "B, " + str(self.endingOffset) + "B)"
    return output
     
  
  def setContributingFilesFromAllFiles(self, allFiles):    
    for payloadFile in allFiles:
      if payloadFile.contributesTo(self):
        contributingFile = FileContributingToPiece.getFromMetafilePieceAndFileObjects(piece=self, file=payloadFile)
        self.contributingFiles.addContributingFile( contributingFile )
  
  def findMatch(self):
    self.logger.debug("Finding match for piece")
    self.logger.debug(self)
    self.contributingFiles.findCombinationThatMatchesReferenceHash( hash=self.hash )
