import itertools
from hashlib import sha1
import logging

class AllContributingFilesToPiece:
  def __init__(self, listOfContributingFiles=None):
    self.listOfContributingFiles = listOfContributingFiles
    self.combinationProducesPositiveHashMatch = None
    self.logger = logging.getLogger("localBFF.libLocalBFF.AllContributingFilesToPiece")
  
  def addContributingFile(self, newFile):
    if self.listOfContributingFiles == None:
      self.listOfContributingFiles = []
    
    self.listOfContributingFiles.append(newFile)
    self.logger.debug("File contributing to piece:")
    self.logger.debug(newFile)
  
  def getNumberOfFiles(self):
    return len(self.listOfContributingFiles)
  
  def findCombinationThatMatchesReferenceHash(self, hash):
    cartesianProductOfPossibleFilePathMatches = self.buildCartesianProductOfPossibleFilePathMatches()
    
    self.logger.debug("Processing through all possible file path combinations...")
    self.logger.debug("Worst-case scenario of all combinations to process: " + str( self.getCardinalityOfCartesianProductOfAllPossibleCombinations() ))
    self.logger.debug("Files contributing to piece: " + str( self.getNumberOfFiles() ))
    
    for combination in cartesianProductOfPossibleFilePathMatches:
      self.logger.debug("Checking combination... ")
      self.logger.debug(combination)
      self.applyCombinationToContributingFiles(combination)
      data = self.getData()
      self.logger.debug("Size of data:\t" + str(len(data)))
      computedHash = sha1(data).digest()
      
      self.combinationProducesPositiveHashMatch = (computedHash == hash)
      
      if self.combinationProducesPositiveHashMatch:
        self.logger.debug("Combination found!")
        self.updateReferenceFilesWithAppropriateMatchedPaths()
        break
      else:
        self.logger.debug("Combination does not match.")
     
    self.updateStatusOfReferenceFiles()
  
  def buildCartesianProductOfPossibleFilePathMatches(self):
    listOfListOfFilePaths = []
    for contributingFile in self.listOfContributingFiles:
      listOfListOfFilePaths.append(contributingFile.getAllPossibleFilePaths())
    
    self.logger.debug("All possible combinations: ")
    self.logger.debug(listOfListOfFilePaths)
    
    cartesianProduct = itertools.product(*listOfListOfFilePaths)
    return cartesianProduct
  
  def getCardinalityOfCartesianProductOfAllPossibleCombinations(self):
    cardinality = 1
    for contributingFile in self.listOfContributingFiles:
      cardinality *= len(contributingFile.referenceFile.possibleMatches)
    
    return cardinality
  
  def applyCombinationToContributingFiles(self, combination):
    for path, contributingFile in zip(combination, self.listOfContributingFiles):
      self.logger.debug("Applying possible path to file...")
      self.logger.debug("Metafile Path: " +contributingFile.referenceFile.getPathFromMetafile())
      self.logger.debug("Possible match Path: " + path)
      contributingFile.possibleMatchPath = path
  
  def getData(self):
    data = ''
    for contributingFile in self.listOfContributingFiles:
      self.logger.debug("Getting data from file: " + contributingFile.possibleMatchPath)
      data += contributingFile.getData()
    
    return data
  
  def updateReferenceFilesWithAppropriateMatchedPaths(self):
    for contributingFile in self.listOfContributingFiles:
      contributingFile.applyCurrentMatchPathToReferenceFileAsPositiveMatchPath()
  
  def updateStatusOfReferenceFiles(self):
    status = ''
    
    if self.combinationProducesPositiveHashMatch:
      status = "MATCH_FOUND"
    else:
      status = "CHECKED_WITH_NO_MATCH"
    
    for contributingFile in self.listOfContributingFiles:
      contributingFile.updateStatus(status)
