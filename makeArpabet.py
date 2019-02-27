# -*- coding: utf-8 -*-

# makeArpabet.py
# Rolando Coto-Solano, Victoria University of Wellington
# Last updated: 20190227
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

def splitWordInSpaces(inWord, langGlyphs, arpaGlyphs):

	digraphsTogether = []
	digraphsExploded = []
	hasNonCIMLetter = 0
	
	#print("inWord: " + inWord + "\n")
	
	totGlyphs = len(langGlyphs)
	for i in range(0,totGlyphs):
		if (len(langGlyphs[i]) > 1):
			digraphsTogether.append(langGlyphs[i])
			digraphsExploded.append(" ".join(langGlyphs[i]))
			
			
	outWord = ""
	outWordWithoutEmptyChars = ""
	
	for c in inWord:
		outWord += c + " "
	outWord = outWord[:-1]
	#print("outWord: " + outWord + "\n")
	
	iteratDigraph = 0
	while (iteratDigraph < len(digraphsTogether)):
		outWord = outWord.replace(digraphsExploded[iteratDigraph],digraphsTogether[iteratDigraph])
		iteratDigraph += 1
		
	outWordExploded = outWord.split(" ")
	for c in outWordExploded:
		#print(c)
		if ( getArpaglyph(c,langGlyphs,arpaGlyphs) != "" ):
			outWordWithoutEmptyChars += c + " "
		else:
			hasNonCIMLetter = 1
	outWordWithoutEmptyChars = outWordWithoutEmptyChars[:-1]
	
	return outWordWithoutEmptyChars, hasNonCIMLetter, inWord

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

def getArpaglyph(glyph, langGlyphs, arpaGlyphs):

	res = ""
	sizeArpa = len(langGlyphs)
	
	for i in range(sizeArpa):
		if (langGlyphs[i] == glyph):
			res = arpaGlyphs[i]
		
	return res
		

def arpabetLeftRight(inWord, langGlyphs, arpaGlyphs):

	totGlyphs = len(langGlyphs)
	lenWord   = len(inWord)
	outWord = ""		# 3-column word
	outArpaWord = ""	# arpaword
	hasNonCIMLetter = 0
	
	iterLeft = 0
	found = 0
	searchStr = inWord
	tempStr = ""
	
	while (len(searchStr) > 0):
		for i in range(0,len(searchStr)):
			if (found == 0):
				tempStr = searchStr[0:len(searchStr)-i]
				if (getArpaglyph(tempStr,langGlyphs,arpaGlyphs) != ""):
					if ( getArpaglyph(tempStr,langGlyphs,arpaGlyphs) != " " ):
						found = 1
						#print("found it\n")
						outWord += tempStr + "|"
						outArpaWord += getArpaglyph(tempStr,langGlyphs,arpaGlyphs) + "|"
						#print("el glifo junto es: " + tempStr)
					else: 
						found = 1
				elif (getArpaglyph(" ".join(tempStr),langGlyphs,arpaGlyphs) != ""):
					found = 1
					outWord += " ".join(tempStr).replace(" ","|") + "|"
					outArpaWord += (getArpaglyph(" ".join(tempStr),langGlyphs,arpaGlyphs)).replace(" ","|") + "|"
		if (found == 0):
			hasNonCIMLetter = 1
		searchStr = searchStr[len(tempStr):]
		found = 0
	
	outWord = outWord[:-1]
	outArpaWord = outArpaWord[:-1]
	print("outword is:\t" + outWord);
	print("outArpaWord is:\t" + outArpaWord);
	if ( hasNonCIMLetter == 1 ):
		print("word with error")

	outWord = outWord.replace("|"," ")
	outArpaWord = outArpaWord.replace("|"," ")
		
	return outWord, outArpaWord, hasNonCIMLetter
		
		
	
	
def arpabet(inWord, langGlyphs, arpaGlyphs):

	totGlyphs = len(langGlyphs)
	word    = splitWordInSpaces(inWord, langGlyphs, arpaGlyphs)[0]
	word    = word.split(" ")
	outWord = ""
	hasNonCIMLetter = splitWordInSpaces(inWord, langGlyphs, arpaGlyphs)[1]
	
	if ( hasNonCIMLetter == 0 ):
	
		arpaGlyph = ""
		foundGlyph = 0
		for letter in word:
			#print("voy a buscar: " +  letter +"\n")
			for i in range(0,totGlyphs):
				if letter == langGlyphs[i]:
					arpaGlyph = arpaGlyphs[i]
					foundGlyph = 1
			if (foundGlyph == 1):
				#print("si entre a foundGlyph. el glifo es " +  arpaGlyph +"\n")
				outWord += arpaGlyph + " "
			else:
				hasNonCIMLetter = 1
				outWord += " "
			foundGlyph = 0

		outWord = outWord[:-1]
	
	else:
	
		#print("si entre a hasNonCIMLetter " + str(hasNonCIMLetter) + " en la palabra " + inWord + "\n")
		outWord = inWord
		
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
	outBadWords      = os.path.join("",sys.argv[7])
	wasDict2ColProvided = False
	wasDict3ColProvided = False

	# open files
	newFile      = open(inFilePath, encoding='utf-8').readlines()
	arpaFile     = open(arpaPath, encoding='utf-8').readlines()
	
	
	if ( dict2ColFilePath == "no2ColDict" ):
		wasDict2ColProvided = False
	else:
		dict2ColFile = open(dict2ColFilePath, encoding='utf-8').readlines()	
		wasDict2ColProvided = True
	
	if ( dict3ColFilePath == "no3ColDict" ):
		wasDict3ColProvided = False
	else :
		dict3ColFile = open(dict3ColFilePath, encoding='utf-8').readlines()
		wasDict3ColProvided = True

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
		langGlyphs.append(arpaEq[0].replace("\r","").replace("\n",""))
		arpaGlyphs.append(arpaEq[1].replace("\r","").replace("\n",""))
		
		
	sizeArpa = len(langGlyphs)
	for i in range(sizeArpa):
		print("arpapair: " + langGlyphs[i] + "-" + arpaGlyphs[i])
		print("arpapair: " + str(len(langGlyphs[i])) + "-" + str(len(arpaGlyphs[i])))
		
	# extract all the unique words in the preexisting dictionary
	allWordsInDict2ColFile = []
	if wasDict2ColProvided == True :
		for line in dict2ColFile:
			line = eliminateExtraChars(line)
			lines2Col.append(line)
			line = line.lower()
			words = line.split("\t")
	
	uniqueWordsIn2ColDict = set(allWordsInDict2ColFile)

	# extract all the lines in the three column dictionary
	if wasDict3ColProvided == True :
		for line in dict3ColFile:
			line = eliminateExtraChars(line)
			lines3Col.append(line)
	else:
		if wasDict2ColProvided == True:
			for line in dict2ColFile:
				line = eliminateExtraChars(line)
				lineWords = line.split("\t")
				generate3ColLine = line + "\t" + arpabetLeftRight(lineWords[0], langGlyphs, arpaGlyphs)[0] + "\r\n"
				lines3Col.append(generate3ColLine)

	# get a list of all new words that are not already in the dictionary
	allWordsInInputAnd2Col = allWordsInInputFile + allWordsInDict2ColFile
	uniqueWordsInInputAnd2Col = set(allWordsInInputAnd2Col)
	wordsMissingInDict = list(uniqueWordsInInputAnd2Col - uniqueWordsIn2ColDict)

	# generate the ARPAbet for each new word
	newLines2Col = []
	newLines3Col = []
	badWords = ""
	for word in wordsMissingInDict:
	
		print(word + "\n")
		print(arpabet(word,langGlyphs,arpaGlyphs)[0] + "\n")
		print(arpabetLeftRight(word,langGlyphs,arpaGlyphs)[0])
		#print(str(arpabet(word,langGlyphs,arpaGlyphs)[1]) + "\n")
	
		if arpabetLeftRight(word,langGlyphs,arpaGlyphs)[2] == 0:
			
			newLines2Col.append(changeInitialAposToQ(word) + "\t" + arpabetLeftRight(word,langGlyphs,arpaGlyphs)[1] + "\r\n")
			newLines3Col.append(changeInitialAposToQ(word) + "\t" + arpabetLeftRight(word,langGlyphs,arpaGlyphs)[1] + "\t" + arpabetLeftRight(word, langGlyphs, arpaGlyphs)[0] + "\r\n")
					
		else:
			badWords += word + "\t" + arpabetLeftRight(word, langGlyphs, arpaGlyphs)[1] + "\t" + arpabetLeftRight(word, langGlyphs, arpaGlyphs)[0] + "\r\n"

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
	out2Col = out2Col.replace("\r\n\r\n", "\r\n")
	out3Col = out3Col.replace("\r\n\r\n", "\r\n")

	# alert the user about possible non-CIM words
	if badWords is not "":
		print("\nThere are non-CIM words. Please see wordsWithoutArpabet.txt")
		open(outBadWords, "wb").write((badWords).encode('utf-8','replace'))

	# print the new 2Col and 3Col files
	open(out2ColPath, "wb").write((out2Col).encode('utf-8','replace'))
	#open(out2ColPath, "wb").write((str(uniqueWordsIn2ColDict)).encode('utf-16','replace'))
	open(out3ColPath, "wb").write((out3Col).encode('utf-8','replace'))
