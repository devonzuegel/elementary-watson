#!/usr/bin/env python
# CS124 Homework 5 Jeopardy
# Original written in Java by Sam Bowman (sbowman@stanford.edu)
# Ported to Python by Milind Ganjoo (mganjoo@stanford.edu)

# There's nothing for you to implement here, hooray!

import urllib
import urllib2
import hashlib
import email
import email.message
import email.encoders
import sys

#URL TO CHANGE EVERY YEAR: portion of URL after https://stanford.coursera.org/
#ie for winter 2014 cs124-002 and winter 2013 cs124-001
BASE_CLASS_URL = "cs124-003"

#boolean for submission testing purposes when assignment hasn't been released to class yet
RELEASED_TO_CLASS = True

def submit(partId):
    print '==\n== [cs124-Winter2014-15] Submitting Solutions | Programming Exercise %s\n=='% homework_id()
    if (not partId):
        partId = promptPart()
    
    partNames = validParts()
    if not isValidPartId(partId):
        print '!! Invalid homework part selected.'
        print '!! Expected an integer from 1 to %d.' % (len(partNames) + 1)
        print '!! Submission Cancelled'
        return
    
    (login, password) = loginPrompt()
    if not login:
        print '!! Submission Cancelled'
        return
    
    print '\n== Connecting to cs124-Winter2013-14 ... '
    
    # Setup submit list
    if partId == len(partNames) + 1:
        submitParts = range(1, len(partNames) + 1)
    else:
        submitParts = [partId]
    
    for partId in submitParts:
        # Get Challenge
        (login, ch, state, ch_aux) = getChallenge(login, partId)
        if((not login) or (not ch) or (not state)):
            # Some error occured, error string in first return element.
            print '\n!! Error: %s\n' % login
            return
        
        # Attempt Submission with Challenge
        ch_resp = challengeResponse(login, password, ch)
        (result, string) = submitSolution(login, ch_resp, partId, output(partId, ch_aux), \
                                          source(partId), state, ch_aux)
        print '\n== [cs124-Winter2014-15] Submitted Homework %s - Part %d - %s' % \
            (homework_id(), partId, partNames[partId - 1]),
        print '== %s' % string.strip()

def promptPart():
    """Prompt the user for which part to submit."""
    print('== Select which part(s) to submit: ' + homework_id())
    partNames = validParts()
    srcFiles = sources()
    for i in range(1,len(partNames)+1):
        print '==   %d) %s [ %s ]' % (i, partNames[i - 1], srcFiles[i - 1])
    print '==   %d) All of the above \n==\nEnter your choice [1-%d]: ' % \
        (len(partNames) + 1, len(partNames) + 1)
    selPart = raw_input('')
    partId = int(selPart)
    if not isValidPartId(partId):
        partId = -1
    return partId


def validParts():
    """Returns a list of valid part names."""
    
    partNames = [ 'Clue Parsing Development', \
                 'Clue Parsing Testing', \
                 'Answer Generation Development', \
                 'Answer Generation Testing'
                 ]
    return partNames


def sources():
    """Returns source files, separated by part. Each part has a list of files."""
    srcs = [ [ 'ClueParser.py'], \
            [ 'ClueParser.py'], \
            [ 'Answerer.py'], \
            [ 'Answerer.py']
            ]
    return srcs

def isValidPartId(partId):
    """Returns true if partId references a valid part."""
    partNames = validParts()
    return (partId and (partId >= 1) and (partId <= len(partNames) + 1))


# =========================== LOGIN HELPERS ===========================

def loginPrompt():
    """Prompt the user for login credentials. Returns a tuple (login, password)."""
    (login, password) = basicPrompt()
    return login, password


def basicPrompt():
    """Prompt the user for login credentials. Returns a tuple (login, password)."""
    login = raw_input('Login (Email address): ')
    password = raw_input('Password: ')
    return login, password


def homework_id():
    """Returns the string homework id."""
    return '6'


def getChallenge(email, partId):
    """Gets the challenge salt from the server. Returns (email,ch,state,ch_aux)."""
    url = challenge_url()
    if RELEASED_TO_CLASS:
        values = {'email_address' : email, 'assignment_part_sid' : "%s-%d" % (homework_id(), partId), 'response_encoding' : 'delim'}
    else:
        values = {'email_address' : email, 'assignment_part_sid' : "%s-%d-dev" % (homework_id(), partId), 'response_encoding' : 'delim'}
    data = urllib.urlencode(values)
    req = urllib2.Request(url, data)
    response = urllib2.urlopen(req)
    text = response.read().strip()
    
    # text is of the form email|ch|signature
    splits = text.split('|')
    if(len(splits) != 9):
        print 'Badly formatted challenge response: %s' % text
        return None
    return (splits[2], splits[4], splits[6], splits[8])

def challengeResponse(email, passwd, challenge):
    sha1 = hashlib.sha1()
    sha1.update("".join([challenge, passwd])) # hash the first elements
    digest = sha1.hexdigest()
    strAnswer = ''
    for i in range(0, len(digest)):
        strAnswer = strAnswer + digest[i]
    return strAnswer



def challenge_url():
    """Returns the challenge url."""
    return 'https://stanford.coursera.org/' + BASE_CLASS_URL + '/assignment/challenge'


def submit_url():
    """Returns the submission url."""
    return 'https://stanford.coursera.org/' + BASE_CLASS_URL + '/assignment/submit'

def submitSolution(email_address, ch_resp, part, output, source, state, ch_aux):
    """Submits a solution to the server. Returns (result, string)."""
    source_64_msg = email.message.Message()
    source_64_msg.set_payload(source)
    email.encoders.encode_base64(source_64_msg)
    
    output_64_msg = email.message.Message()
    output_64_msg.set_payload(output)
    email.encoders.encode_base64(output_64_msg)
    if RELEASED_TO_CLASS:
        values = { 'assignment_part_sid' : ("%s-%d" % (homework_id(), part)), \
            'email_address' : email_address, \
            #'submission' : output, \
            'submission' : output_64_msg.get_payload(), \
            #'submission_aux' : source, \
            'submission_aux' : source_64_msg.get_payload(), \
            'challenge_response' : ch_resp, \
            'state' : state \
        }
    else:
        values = { 'assignment_part_sid' : ("%s-%d-dev" % (homework_id(), part)), \
            'email_address' : email_address, \
            #'submission' : output, \
            'submission' : output_64_msg.get_payload(), \
            #'submission_aux' : source, \
            'submission_aux' : source_64_msg.get_payload(), \
            'challenge_response' : ch_resp, \
            'state' : state \
        }
    
    url = submit_url()
    data = urllib.urlencode(values)
    req = urllib2.Request(url, data)
    response = urllib2.urlopen(req)
    string = response.read().strip()
    # TODO parse string for success / failure
    result = 0
    return result, string

def source(partId):
    """Reads in the source files for a given partId."""
    src = ''
    src_files = sources()
    if partId <= len(src_files):
        flist = src_files[partId - 1]
        for fname in flist:
            # open the file, get all lines
            f = open(fname)
            src = src + f.read()
            f.close()
            src = src + '||||||||'
    return src

############ BEGIN ASSIGNMENT SPECIFIC CODE ##############

from ClueParser import ClueParser
from Answerer import Answerer
from ClueParser import loadList
import itertools as it

def gradeClueParser(partId, ch_aux):
    clueParser = ClueParser()
    clues = []
    cluesFile = "../data/part1-clues.txt"
    parsedCluesFile = "../data/part1-parsedclues.txt"
    
    clues = loadList(cluesFile)
    goldParsedClues = loadList(parsedCluesFile)
    clueParser.train(clues, goldParsedClues)
    
    if partId == 2:
        clues = ch_aux.split("\n")
    
    parses = clueParser.parseClues(clues)
    
    if (partId == 1):
        score = evaluateParses(parses, goldParsedClues)
        return "{0}".format(score)
    else:
        return encodeClueParser(parses)

def evaluateParses(parsed_clues, gold_parsed_clues):
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
    
    return correct_relations + correct_parses

def packageClueParser(parses):
    result = ""
    for parse in parses:
        result += parse
        result += "##"
    return result[:-2]

def encodeClueParser(parses):
    try:
        import json
        res_json = json.dumps([parses])
    except ImportError:
        sys.stederr.write('!!! Error importing json library. This is likely due to an early version of Python 2.6. Attempting to submit without json library. If this fails, please update to Python 2.7.')
        res_json = str([parses])
        res_json = res_json.replace('\'', '\"')
    finally:
        return res_json

def encodeAnswerer(guessedAnswers, guessedAnswersFromParses):
    try:
        import json
        res_json = json.dumps([guessedAnswers, guessedAnswersFromParses])
    except ImportError:
        sys.stderr.write('!!! Error importing json library. This is likely due to an early version of Python 2.6. Attempting to submit without json library. If this fails, please update to Python 2.7.')
        res_json = str([guessedAnswers, guessedAnswersFromParses])
        res_json = res_json.replace('\'', '\"')
    finally:
        return res_json

def output(partId, ch_aux):
    original_stdout = sys.stdout
    sys.stdout = NullDevice()
    
    out = None
    if partId == 1 or partId == 2:
        score = gradeClueParser(partId, ch_aux)
        out = "part[%d][%s" % (partId, str(score))
    elif partId == 3 or partId == 4:
        score = gradeAnswerer(partId, ch_aux)
        out = "part[%d][%s" % (partId, str(score))
    else:
        sys.stderr.write("Unknown partId: %d" % (partId))
    
    sys.stdout = original_stdout
    return out

class NullDevice():
    def write(self, s):
        pass

def gradeAnswerer(partId, ch_aux):
    answerer = Answerer()
    guessedParses = None
    guessedAnswers = None
    guessedAnswersFromParses = None
    goldAnswers = None
    
    cp = ClueParser()
    trCluesFile = "../data/part1-clues.txt"
    trParsedCluesFile = "../data/part1-parsedclues.txt"
    trClues = loadList(trCluesFile)
    trGoldParsedClues = loadList(trParsedCluesFile)
    cp.train(trClues, trGoldParsedClues)
    
    if partId == 3:
        parsesFile = "../data/part2-parses.txt"
        goldFile = "../data/part2-gold.txt"
        cluesFile = "../data/part2-clues.txt"
        clues = loadList(cluesFile)
        
        # Test on unparsed questions.
        guessedParses = cp.parseClues(clues)
        guessedAnswers = answerer.answer(guessedParses)
        
        # Test on parsed questions.
        goldParses = loadList(parsesFile)
        guessedAnswersFromParses = answerer.answer(goldParses)
        goldAnswers = loadList(goldFile)
    elif partId == 4:
        lines = ch_aux.splitlines()
        spl = 15
        clues = lines[:spl]
        
        # Test on unparsed questions.
        guessedParses = cp.parseClues(clues)
        guessedAnswers = answerer.answer(guessedParses)
        
        # Test on parsed questions.
        goldParses = lines[spl:]
        guessedAnswersFromParses = answerer.answer(goldParses)
    
    if partId == 3:
        return "{0}".format(evaluateAnswerSet(guessedAnswers, goldAnswers) + evaluateAnswerSet(guessedAnswersFromParses, goldAnswers))
    else:
        return encodeAnswerer(guessedAnswers, guessedAnswersFromParses)

def evaluateAnswerSet(guessed_answers, gold_answers):
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
    
    return score

if __name__ == '__main__':
    submit(0)
