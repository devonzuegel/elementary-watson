#!/usr/bin/env python
# CS124 Homework 5 Jeopardy
# Original written in Java by Sam Bowman (sbowman@stanford.edu)
# Ported to Python by Milind Ganjoo (mganjoo@stanford.edu)

from ClueParser import ClueParser
from GenderClassifier import GenderClassifier
import itertools as it
import re
import pprint

pp = pprint.PrettyPrinter(indent=4)
proper_noun = '((?:[A-Z]\w+ )*[A-Z]\w+)'
person_name = '<PERSON>%s</PERSON>' % (proper_noun)

class Answerer:
  # Answer each clue and return a list of answers.
  def answer(self, parsed_clues):
    answers = []
    gc = GenderClassifier()
    wiki_filename = '../data/wiki-text-ner.txt'
    ##
    # Build array of docs split on the <TITLE> tag (which occurs at
    # beginning of every doc)
    all_docs = '  '.join(loadList(wiki_filename)).split('<TITLE>')

    # ##
    #   # TODO: Process the wiki file and fill in the answers list.
    #   # Add 'No answer.' as the answer when you don't find an answer
    #   # you are confident of. We recommend using Hearst style
    #   # patterns to find answers within the Wiki text.
    for parsed_clue in parsed_clues:
      clue_type, clue_entity = parsed_clue.split(':')
      
      # def clue_regex_in_doc():
      #   bool(re.search(regex, ))
     
      relevant_docs = [d for d in all_docs if clue_entity in d]
      # TODO: DEALS WITH THIS CASE ("Ike Eisenhower" is in 0 docs)
      if len(relevant_docs) == 0:
        for word in clue_entity.split():
          relevant_docs += [d for d in all_docs if word in d]
      
      if clue_type == 'year_of_birth':  # ex: 'What is 1957?'
        answers.append(self.answerYOB(clue_entity, relevant_docs))
      elif clue_type == 'born_in':      # ex: 'What is Paris?'
        answers.append(self.answerBornIn(clue_entity, relevant_docs))
      elif clue_type == 'husband_of':   # ex: 'Who is Anne Hathaway?'
        answers.append(self.answerHusbandOf(clue_entity, relevant_docs))
      else:
        answers.append('No answer.')

    print '\n'
    for i, parsed_clue in enumerate(parsed_clues):
      print '%d  :  %s  :  %s' % (i, parsed_clue, answers[i])

    return answers
  
  # Answers questions of the type husband_of:[clue].
  def answerHusbandOf(self, clue, relevant_docs):
    patterns = [
      r'%s.* wife %s' % (person_name, person_name),
      r'^<PERSON>(.*)</PERSON></TITLE>',
      r'<PERSON>(.*)</PERSON>'
    ]

    # Extract best match m from relevant docs.
    m = self.searchForPatterns(patterns, [1]*len(patterns), relevant_docs)
    if m == None:   return 'No answer.'
    else:           return 'Who is %s?' % (m)

  # Answers questions of the type year_of_birth:[clue].
  def answerYOB(self, clue, relevant_docs):
    
    # 'Katherine [\w ]{1,20} Schwarzenegger[\w<>/]{1,20} \(born \w{1,11} \d{1,2},? (\d{4})'
      # name_clue = r''
      # for name in clue.split():
      #   name_clue += name + '[\w <>/]{1,20}'
      # name_clue += '\([born] \w{1,11} \d{1,2},? (\d{4})'
      # print name_clue

    patterns = [
      # (born Month DD, YYYY DD Month YYYY)
      r'\((?:born )?\b\w{1,11}\b \d{1,2}, (\d{4}) \b\w{1,11}\b \d{1,2}, (\d{4})\)',
      
      # (born DD Month YYYY DD Month YYYY)
      r'\((?:born )?\d{1,2} \b\w{1,11}\b (\d{4}) \d{1,2} \b\w{1,11}\b \d{4}\)',

      # # (born DD Month YYYY DD Month YYYY)
      r'\((?:born )?\d{1,2} \b\w{1,11}\b (\d{4})\)',
      
      # (born DD Month YYYY DD Month YYYY)
      # r'\((?:born )?\b[A-Z]\w{1,10}\b \d{1,2}, (\d{4})\)',
      # (born October 26, 1962)

      # DDDD
      r'(\d{4})'
    ]
    match = self.searchForPatterns(patterns, [1]*len(patterns), relevant_docs)
    
    if match == None:   
      return 'No answer.'
    else:               
      # print 'What is %s?' % (match)
      return 'What is %s?' % (match)

  # Answers questions of the type year_of_birth:[clue].
  def answerBornIn(self, clue, relevant_docs):
    
    patterns = [
      r'was born in <LOCATION>([\w ]+</LOCATION>, <LOCATION>[\w ]+)</LOCATION>',
    ]
    match = self.searchForPatterns(patterns, [1]*len(patterns), relevant_docs)
    match = str(match).replace('<LOCATION>', '').replace('</LOCATION>', '')
    if match == None or match == 'None':
      return 'No answer.'
    else:               
      # print 'What is %s?' % (match)
      return 'What is %s?' % (match)


  ##
    # Searches a text file using several regular expressions at the
    # same time, and returns one match. If more than one regular
    # expression matches a piece of the file, the order of the
    # regular expressions in the list is used to decide which match
    # to return, so you should place more precise regular expressions
    # earlier in the list. If more than one piece of the file
    # matches the same regular expression, the last match in the
    # file will be returned.
  ##
    # ARGUMENTS:
    # > 'patternStrings' should be a list of regular experessions,
    #   ordered from most precise to least precise.
    # > 'patternPositions' should be a list of integers of the same
    #   length as the list of regular expressions and should indicate
    #   which group within each regular expression should be returned.
    #   Group 0 contains the entire match, group 1 contains the piece
    #   of the match inside first set of parantheses of the regular
    #   expression, group 2 contains the piece inside the second set
    #   of parentheses, etc.
    # > 'filename' is the name for the text file being searched.
  ##
    # For example, for the regular expression "He was
    # (maybe|probably) born in (\\d\\d\\d\\d)" and a file with the
    # line "He was maybe born in 1899, and died in 1867.", these
    # will be the groups you can choose from:
    # - Group 0: "He was maybe born in 1899"
    # - Group 1: "maybe"
    # - Group 2: "1899"
  ##
    # So if "1899" is the string that you want to include in your
    # Jeopardy answer, you set the entry in patternPositions
    # corresponding to this regular exrpession to 2.
  def searchForPatterns(self, pattern_strings, pattern_positions, relevant_docs):
    patterns = []
    for pattern_string in pattern_strings:
      patterns.append(re.compile(pattern_string, re.IGNORECASE))
    
    matched_groups = {}
    for doc in relevant_docs:
      for i, p in enumerate(patterns):
        m = p.search(doc)
        if m:
          match = m.group(pattern_positions[i])
          matched_groups[i] = match

    # Return match corresponding to first regex in list.
    if len(matched_groups) > 0:
      return matched_groups[min(matched_groups.keys())]
    else:
      return None
  
  #### You should not need to change anything after this point. ####

  def evaluate(self, guessed_answers, guessed_answers_from_parses, gold_answers):
    """Shows you how your model will score on the training/development data."""
    print "Guessed answers from clues:"
    score1 = self.evaluateAnswerSet(guessed_answers, gold_answers);
    print "Guessed answers from gold parses:"
    score2 = self.evaluateAnswerSet(guessed_answers_from_parses, gold_answers);
    print "Total score: {0}".format(score1 + score2)
  
  def evaluateAnswerSet(self, guessed_answers, gold_answers):
    """Scores one set of answers."""
    correct = 0
    wrong = 0
    no_answers = 0
    score = 0
    
    for guessed_answer, gold_answer_line in it.izip(guessed_answers, gold_answers):
      example_wrong = True # guilty until proven innocent
      if guessed_answer == "No answer.":
        example_wrong = False
        no_answers += 1
      else:
        golds = gold_answer_line.split("|")
        for gold in golds:
          if guessed_answer == gold:
            correct += 1
            score += 1
            example_wrong = False
            break
      if example_wrong:
        wrong += 1
        score -= 0.5
    print "Correct Answers: {0}".format(correct)
    print "No Answers: {0}".format(no_answers)
    print "Wrong Answers: {0}".format(wrong)
    print "Score: {0}".format(score)
    
    return score

def loadList(file_name):
  """Loads text files as lists of lines. Used in evaluation."""
  with open(file_name) as f:
    l = [line.strip() for line in f]
  return l

def main():
  """Tests the model on the command line. This won't be called in
    scoring, so if you change anything here it should only be code
    that you use in testing the behavior of the model."""
  clues_file = "../data/part2-clues.txt"
  parses_file = "../data/part2-parses.txt"
  gold_file = "../data/part2-gold.txt"
  
  training_clues_file = "../data/part1-clues.txt"
  training_parsed_clues_file = "../data/part1-parsedclues.txt"
  
  a = Answerer()
  
  # Test on unparsed questions.
  clues = loadList(clues_file)
  training_clues = loadList(training_clues_file)
  training_parsed_clues = loadList(training_parsed_clues_file)
  
  cp = ClueParser()
  cp.train(training_clues, training_parsed_clues)
  guessed_parses = cp.parseClues(clues)
  guessed_answers = a.answer(guessed_parses)
  
  # Test on parsed questions.
  gold_parses = loadList(parses_file)
  guessed_answers_from_parses = a.answer(gold_parses)
  
  # Evaluate both sets of answers.
  gold_answers = loadList(gold_file)
  a.evaluate(guessed_answers, guessed_answers_from_parses, gold_answers)

if __name__ == '__main__':
  main()
