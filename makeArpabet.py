
# makeArpabet.py
# Rolando Coto-Solano, Victoria University of Wellington
# Last updated: 20181201
#
# This script takes a tab-separated transcription (as generated
# by ELAN or as done manually to use as input for FAVEalign),
# finds words that are not in the dictionary, generates
# an automatic ARPAbet transcription and outputs a new dictionary.
#
# --- Inputs ---
#
# (1) A UTF-8 transcription file adequate for FAVEalign input. This file
# has four tab-separated columns:
# bantha	bantha	2.23	2.70	a
# bantha	bantha	4.09	4.59	i
# bantha	bantha	8	9	tenge
#
# (2) Arpabet equivalence text file. This file has two tab-separated
# columns: the first one has the glyphs in the script of the language,
# and the second column has an ARPAbet equivalence:
# a	AE1
# ā	AE1
# e	EH1
# ē	EH1
# i	IY1
# ī	IY1
# ...
#
# (3) Previously existing Arpabet dictionary. This has two tab-separated
# columns: The first one has the word in the language's script, and the
# second one has the Arpabet transcription. This is the kind of dictionary
# file that FAVEalign takes as input when you want to use "words out of the
# dictionary":
# a	AH1
# i	IY1
#
# (4) Previously existing "three column" Arpabet dictionary. This file
# has three tab-separated columns: The first and second one are identical
# to a FAVEalign dictionary. The third column has the word in the language's
# script, but the glyphs are separated by spaces. This is so that we can
# automatically replace the FAVEalign output with the language's script
# and recover any distinctions we were forced to collapse when using the
# English Arpabet.
# a	AH1	a
# i	IY1	i
#
# (5) Name of the file where the two-column Arpabet dictionary
# will be written.
#
# (6) Name of the file where the three-column Arpabet dictionary 
# will be written.
# 
# --- Outputs ---
#
# (1) A new Arpabet dictionary with two-columns. This program 
# will scan the transcription file for any words that are not
# in the previous dictionary. It will then generate an automatic
# Arpabet transcription for the new words and include them in the
# new dictionary.
# a	AH1
# i	IY1
# tenge	T EH1 NG EH1
#
# (2) A "three-column" Arpabet dictionary. This is identical to
# the two-column one, but it has an additional third column where
# the characters of the language's script are separate by spaces.
# a	AH1	a
# i	IY1	i
# tenge	T EH1 NG EH1	t e ng e
#==================================================================

import os
import string
from xml.dom import minidom
import sys

def changeMacronForX(inWord):
	res = inWord
	res = res.replace("ā","ax")
	res = res.replace("ē","ex")
	res = res.replace("ī","ix")
	res = res.replace("ō","ox")
	res = res.replace("ū","ux")
	return res

def splitWordInSpaces(inWord, langGlyphs):

	digraphsTogether = []
	digraphsExploded = []
	
	tempDigraph = ""
	totGlyphs = len(langGlyphs)
	for i in range(0,totGlyphs):
		if len(langGlyphs[i]) > 1:
			for c in langGlyphs[i]:
				tempDigraph += c + " "
			tempDigraph = tempDigraph[:-1]
			digraphsTogether.append(langGlyphs[i])
			digraphsExploded.append(tempDigraph)
			tempDigraph = ""

	outWord = ""
	for c in inWord:
		outWord += c + " "
	outWord = outWord[:-1]
	outWord = outWord.replace("n g", "ng")

	return outWord

def changeInitialAposToQ(inWord):

	retWord = ""
	if (inWord[0] == "'"):
		retWord = "q" + inWord[1:]
	else:
		retWord = inWord
	return retWord

def changeInitialQToApos(inWord):

	retWord = ""
	if (inWord[0] == "q"):
		retWord = "'" + inWord[1:]
	else:
		retWord = inWord
	return retWord


	
def arpabet(inWord, langGlyphs, arpaGlyphs):

	totGlyphs = len(langGlyphs)
	word    = splitWordInSpaces(inWord, langGlyphs)
	word    = word.split(" ")
	outWord = ""
	hasNonCIMLetter = 0
	
	arpaGlyph = ""
	foundGlyph = 0
	for letter in word:
		for i in range(0,totGlyphs):
			if letter == langGlyphs[i]:
				arpaGlyph = arpaGlyphs[i]
				foundGlyph = 1
		if (foundGlyph == 1):
			outWord += arpaGlyph + " "
		else:
			hasNonCIMLetter = 1
			outWord += " "
		foundGlyph = 0

	outWord = outWord[:-1]
	return outWord, hasNonCIMLetter

def eliminateExtraChars(inLine):
	inLine = inLine.replace("\n", "")
	inLine = inLine.replace("\r", "")
	inLine = inLine.replace("ꞌ", "'")
	inLine = inLine.replace(",", "")
	inLine = inLine.replace(".", "")
	inLine = inLine.replace("?", "")
	return inLine

if __name__ == "__main__":

	inFilePath       = os.path.join("",sys.argv[1])
	arpaPath         = os.path.join("",sys.argv[2])
	dict2ColFilePath = os.path.join("",sys.argv[3])
	dict3ColFilePath = os.path.join("",sys.argv[4])
	out2ColPath      = os.path.join("",sys.argv[5])
	out3ColPath      = os.path.join("",sys.argv[6])
	outBadWords      = os.path.join("","wordsWithoutArpabet.txt")

	# open files
	newFile      = open(inFilePath,       encoding='utf-8').readlines()
	arpaFile     = open(arpaPath,         encoding='utf-8').readlines()
	dict2ColFile = open(dict2ColFilePath, encoding='utf-8').readlines()
	dict3ColFile = open(dict3ColFilePath, encoding='utf-8').readlines()

	out = ""
	lines2Col = []
	lines3Col = []
	out2Col = ""
	out3Col = ""

	# extract all the unique words in the input file
	allWordsInInputFile = []
	for line in newFile:
		line = line.split("\t")[4]
		line = eliminateExtraChars(line)
		line = line.lower()
		words = line.split(" ")
		allWordsInInputFile += words
	uniqueWordsInInput = set(allWordsInInputFile)
	
	# make the Arpabet
	langGlyphs = []
	arpaGlyphs = []
	for line in arpaFile:
		arpaEq = line.split("\t")
		langGlyphs.append(arpaEq[0])
		arpaGlyphs.append(arpaEq[1].replace("\r","").replace("\n",""))
		
	# extract all the unique words in the preexisting dictionary
	allWordsInDict2ColFile = []
	for line in dict2ColFile:
		line = eliminateExtraChars(line)
		lines2Col.append(line)
		line = line.lower()
		words = line.split("\t")
		allWordsInDict2ColFile.append(changeInitialQToApos(words[0]))
	uniqueWordsIn2ColDict = set(allWordsInDict2ColFile)

	# extract all the lines in the three column dictionary
	for line in dict3ColFile:
		line = eliminateExtraChars(line)
		lines3Col.append(line)

	# get a list of all new words that are not already in the dictionary
	allWordsInInputAnd2Col = allWordsInInputFile + allWordsInDict2ColFile
	uniqueWordsInInputAnd2Col = set(allWordsInInputAnd2Col)
	wordsMissingInDict = list(uniqueWordsInInputAnd2Col - uniqueWordsIn2ColDict)

	# generate the ARPAbet for each new word
	newLines2Col = []
	newLines3Col = []
	badWords = ""
	for word in wordsMissingInDict:
		if arpabet(word,langGlyphs,arpaGlyphs)[1] == 0:
			newLines2Col.append(changeInitialAposToQ(word) + "\t" + arpabet(word,langGlyphs,arpaGlyphs)[0] + "\r\n")
			newLines3Col.append(changeInitialAposToQ(word) + "\t" + arpabet(word,langGlyphs,arpaGlyphs)[0] + "\t" + splitWordInSpaces(word, langGlyphs) + "\r\n")
		else:
			badWords += word + "\t" + splitWordInSpaces(word, langGlyphs) + "\r\n"

	# insert the new words in the 2Col and 3Col dictionaries
	lines2Col += newLines2Col
	lines3Col += newLines3Col

	# arrange 2Col and 3Col lists alphabetically
	lines2Col.sort()
	lines3Col.sort()

	# prepare to print 2Col and 3Col to files
	for line in lines2Col:
		out2Col += line + "\r\n"
	for line in lines3Col:
		out3Col += line + "\r\n"
	#out2Col = out2Col.replace("\n\n", "\n")
	out2Col = out2Col.replace("\r\n\r\n", "\r\n")
	#out3Col = out3Col.replace("\n\n", "\n")
	out3Col = out3Col.replace("\r\n\r\n", "\r\n")

	# alert the user about possible non-CIM words
	if badWords is not "":
		print("\nThere are non-CIM words. Please see wordsWithoutArpabet.txt")

	
	out2Col = changeMacronForX(out2Col)
	out3Col = changeMacronForX(out3Col)
		
	# print the new 2Col and 3Col files
	open(out2ColPath, "wb").write((out2Col).encode('utf-8','replace'))
	#open(out2ColPath, "wb").write((str(uniqueWordsIn2ColDict)).encode('utf-16','replace'))
	open(out3ColPath, "wb").write((out3Col).encode('utf-8','replace'))
	open(outBadWords, "wb").write((badWords).encode('utf-8','replace'))