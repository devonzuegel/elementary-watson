#!/usr/bin/env python
# CS124 Homework 5 Jeopardy
# Original written in Java by Sam Bowman (sbowman@stanford.edu)
# Ported to Python by Milind Ganjoo (mganjoo@stanford.edu)

import itertools as it
from NaiveBayes import NaiveBayes
import re

def p(s1, s2):
  print s1
  print s2
  print '\n'

class ClueParser:
  def __init__(self):
    # Declares a trained classifier.
    self.classifier = NaiveBayes()
    self.stopWords = set(self.readFile('../data/english.stop'))
    self.types = [
      'headquarters_loc', 
      'wife_of', 
      'univ_in', 
      'mayor_of', 
      'year_of_birth', 
      'parent_org_of', 
      'husband_of', 
      'born_in', 
      'univ_president_of', 
      'college_of', 
      'year_of_death'
    ]

  def extract_features(self, clue):
    # # Remove all stop words from the clue
      # # TODO: Work slightly better if we don't remove stopWords...?!?!
      # clue_no_stops = ' '.join([w for w in clue.lower().split() if w not in self.stopWords])
    # Extract into list

    ##
    # We don't want to lowercase our clues here b/c this method
    # is also used for parseClues, which is case sensitive.
    # Instead, .lowercase() features lists after extraction for
    # specific use cases (like classification).
    features = re.findall(r"[\w'-]+", clue)

    return features

  def person_name(self, features):
    name = []
    in_person_tag = False
    for f in features:
      if in_person_tag:   
        if f == 'PERSON':
          return (' ').join(name)
        name.append(f)
      elif f == 'PERSON':   in_person_tag = True


      # if not in_person_tag and len(name) > 0:
      #   print name
        

  # Parse each clue and return a list of parses, one for each clue."""
  def parseClues(self, clues):
    parses = []
    for clue in clues:
      features = self.extract_features(clue)
      klass = self.classifier.classify([w.lower() for w in features])
      parse = ''
      
      if klass == 'headquarters_loc': # organization name (all words start with caps maybe?)
        # parse = 'Information Habitat'
        parse = ''

      if klass == 'wife_of': # man's name (<PERSON></PERSON> + use gender classifier)
        # parse = 'George Fenneman'
        parse = self.person_name(features)

      if klass == 'univ_in': # 'town, city' in format 'w+, \w{2,}'
        parse = ''

      if klass == 'mayor_of': # 'town, city' in format 'w+, \w{2,}'
        parse = ''

      if klass == 'year_of_birth': # person's name (<PERSON></PERSON>)
        parse = self.person_name(features)

      if klass == 'parent_org_of': # Find organization name (all words start with caps maybe?)
        # parse = 'Alive & Well AIDS Alternatives'
        parse = ''

      if klass == 'husband_of': # woman's name (<PERSON></PERSON> + use gender classifier)
        parse = self.person_name(features)

      if klass == 'born_in': # person's name (<PERSON></PERSON>)
        parse = self.person_name(features)

      if klass == 'univ_president_of': # college/university (ends with 'College', 'Uni..', all caps)
        # parse = 'Western State Colorado University'
        parse = ''
      
      if klass == 'college_of':  # person's name (<PERSON></PERSON>)
        parse = self.person_name(features)
      
      if klass == 'year_of_death': # person's name (<PERSON></PERSON>)
        parse = self.person_name(features)
      
      parses.append('%s:%s' % (klass, parse))

      p(features, parses[-1])

    # print parses
    return parses

  # Trains the model on clues paired with gold standard parses.
  def train(self, clues, parsed_clues):
    # NOTE: len(clues) == len(parsed_clues)
    features_list = [0]*len(clues)
    labels = [0]*len(parsed_clues)

    # Iterate through each clue
    for i, clue in enumerate(clues):
      # Extract case-sensitive features from clue
      features = self.extract_features(clue)

      # .lowercase() list of features before appending to features_list
      features_list[i] = [w.lower() for w in features]

    for i, parsed_clue in enumerate(parsed_clues):
      labels[i] = parsed_clue.split(':')[0]

    self.classifier.addExamples(features_list, labels);


  #########################################################################
  #### You should not need to change anything after this point. ###########
  #########################################################################

  ##
  # Code for reading a file.  you probably don't want to modify anything
  # here, unless you don't like the way we segment files.
  def readFile(self, fileName):
    contents = []
    f = open(fileName)
    for line in f:
      contents.append(line)
    f.close()
    result = self.segmentWords('\n'.join(contents)) 
    return result

  # Splits lines on whitespace for file reading  
  def segmentWords(self, s):
    return s.split()

  def evaluate(self, parsed_clues, gold_parsed_clues):
    """Shows how the ClueParser model will score on the training/development data."""
    correct_relations = 0
    correct_parses = 0
    for parsed_clue, gold_parsed_clue in it.izip(parsed_clues, gold_parsed_clues):
      split_parsed_clue = parsed_clue.split(":")
      split_gold_parsed_clue = gold_parsed_clue.split(":")
      if split_parsed_clue[0] == split_gold_parsed_clue[0]:
        correct_relations += 1
        if (split_parsed_clue[1] == split_gold_parsed_clue[1] or
            split_parsed_clue[1] == "The " + split_gold_parsed_clue[1] or
            split_parsed_clue[1] == "the " + split_gold_parsed_clue[1]):
          correct_parses += 1
    print "Correct Relations: %d/%d" % (correct_relations, len(gold_parsed_clues))
    print "Correct Full Parses: %d/%d" % (correct_parses, len(gold_parsed_clues))
    print "Total Score: %d/%d" % (correct_relations + correct_parses, 2 * len(gold_parsed_clues))

def loadList(file_name):
  """Loads text files as lists of lines. Used in evaluation."""
  with open(file_name) as f:
    l = [line.strip() for line in f]
  return l

def main():
  """Tests the model on the command line. This won't be called in
    scoring, so if you change anything here it should only be code 
    that you use in testing the behavior of the model."""

  clues_file = "../data/part1-clues.txt"
  parsed_clues_file = "../data/part1-parsedclues.txt"
  cp = ClueParser()

  clues = loadList(clues_file)
  gold_parsed_clues = loadList(parsed_clues_file)
  assert(len(clues) == len(gold_parsed_clues))

  cp.train(clues, gold_parsed_clues)
  parsed_clues = cp.parseClues(clues)
  cp.evaluate(parsed_clues, gold_parsed_clues)

if __name__ == '__main__':
  main()
# 