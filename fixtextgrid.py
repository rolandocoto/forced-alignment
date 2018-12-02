# -*- coding: utf-8 -*-
#========================================================================
# fixtextgrid.py
# Rolando Coto-Solano. Victoria University of Wellington
# Last update: December 2nd, 2018
#
# This program takes a TextGrid (the output of FAVEalign) and replaces
# the Arpabet characters with the in-language characters for each word,
# as specified in the three-column dictionary.
#
# --- Inputs ---
# 
# (1) A TextGrid with two tiers, the first one with Arpabet phones, 
# and the second one with words. This is the output of FAVEalign.
# Therefore, the intervals that contain the phones for each word (in
# tier 1) are all contained within the time of the interval that
# contains the word (tier 2).
# 
# (2) A three-column dictionary. The first and second one are identical
# to a FAVEalign dictionary. (The first one has the word in the
# language's script, the second one has the Arpabet transcription).
# The third column has the word in the language's script, but the
# glyphs are separated by spaces. This is so that we can automatically
# replace the FAVEalign output with the language's script and recover
# any distinctions we were forced to collapse when using the English
# Arpabet.
# a	AH1	a
# i	IY1	i
#
# (3) The path where the new TextGrid will be written.
#
# --- Outputs ---
#
# (1) A FAVEalign TextGrid where the Arpabet in the first tier
# has been replaced with glyphs of the language's alphabet.
#========================================================================

import os
import string
from xml.dom import minidom
import sys

if __name__ == "__main__":

	tgPath = os.path.join("",sys.argv[1])
	dictPath = os.path.join("",sys.argv[2])  # Three-column dictionary
	outPath = os.path.join("",sys.argv[3])  # Output path
	
	tgFile = open(tgPath, encoding='utf-8').readlines()
	dict = open(dictPath, encoding='utf-8').readlines()
	
	lineNum = 0
	totLines = len(tgFile)
	
	header = ""
	midFile = ""
	
	t1xminLine = []
	t1xmin = []
	t1xmaxLine = []
	t1xmax = []
	t1text = []
	t1intervalID = []
	t2xminLine = []
	t2xmin = []
	t2xmaxLine = []
	t2xmax = []
	t2text = []
	t2intervalID = []
	
	# Extract the words from the three-column dictionary
	
	dictWord = []
	dictArpa = []
	dictTriWord = []
	for line in dict:
		line = line.split("\t")
		dictWord.append(line[0].replace("\r","").replace("\n",""))
		dictArpa.append(line[1].replace("\r","").replace("\n","").split(" "))
		dictTriWord.append(line[2].replace("\r","").replace("\n","").split(" "))
	
	# Extract the header of the TextGrid
	
	while ("intervals: size" not in tgFile[lineNum]):
		header = header + tgFile[lineNum]
		lineNum = lineNum + 1
	header = header + tgFile[lineNum]
	lineNum = lineNum + 1
	
	# Extract the phone intervals (first tier)
	
	while ("item [2]:" not in tgFile[lineNum]):
		t1intervalID.append(tgFile[lineNum])
		lineNum = lineNum + 1
		t1xminLine.append(tgFile[lineNum])
		t1xmin.append(float(tgFile[lineNum][11:-1]))
		lineNum = lineNum + 1
		t1xmaxLine.append(tgFile[lineNum])
		t1xmax.append(float(tgFile[lineNum][11:-1]))
		lineNum = lineNum + 1
		t1text.append(tgFile[lineNum][12:-2])
		lineNum = lineNum + 1
	
	# Extract the middle part of the TextGrid, the transition
	# between the first and second tiers.
	
	midFile = midFile + tgFile[lineNum]
	while ("intervals: size" not in tgFile[lineNum]):
		midFile = midFile + tgFile[lineNum]
		lineNum = lineNum + 1
	midFile = midFile + tgFile[lineNum]
	lineNum = lineNum + 1
	
	# Extract the word intervals (second tier)
	
	while (lineNum < totLines):
		t2intervalID.append(tgFile[lineNum])
		lineNum = lineNum + 1
		t2xminLine.append(tgFile[lineNum])
		t2xmin.append(float(tgFile[lineNum][11:-1]))
		lineNum = lineNum + 1
		t2xmaxLine.append(tgFile[lineNum])
		t2xmax.append(float(tgFile[lineNum][11:-1]))
		lineNum = lineNum + 1
		t2text.append(tgFile[lineNum][12:-2])
		lineNum = lineNum + 1
	
	# We look for which phone intervals (intervals in the first tier) are
	# contained in time by word intervals (intervals in the second tier).
	
	wordNum = 0
	phoneNum = 0
	tempIntervals = []
	phonesInWord = []
	while (wordNum < len(t2text)):
		while (phoneNum < len(t1text)):
			if (t1xmin[phoneNum] >= t2xmin[wordNum] and t1xmax[phoneNum] <= t2xmax[wordNum]):
				tempIntervals.append(phoneNum)
			phoneNum = phoneNum + 1
		phonesInWord.append(tempIntervals)
		tempIntervals = []
		phoneNum = 0
		wordNum = wordNum + 1
	
	# Look for the words in the dictionary. If the word exists, and if there are as many segments
	# in the phone tiers as there are characters in the third column of the three-column entry
	# for the word, then each of the Arpabet characters is replaced by the characters in the 
	# three-column entry. For example:
	# 
	# t1text		t1outtext
	# T				t
	# EH1			e
	# NG			ng
	# EH1			e
	
	wordNum = 0
	dictNum = 0
	coordNum = 0
	t1outtext = t1text
	
	while (wordNum < len(t2text)):
		while (dictNum < len(dictTriWord)):
			if (dictWord[dictNum].lower() == t2text[wordNum].lower() and len(dictWord[dictNum]) == len(t2text[wordNum])):
				while coordNum < len(phonesInWord[wordNum]):
					t1outtext[phonesInWord[wordNum][coordNum]] = dictTriWord[dictNum][coordNum]
					coordNum = coordNum + 1
				coordNum = 0
			dictNum = dictNum+1
		dictNum = 0
		wordNum = wordNum + 1
	
	# Write the output TextGrid
	
	out = header
	
	phoneNum = 0
	while phoneNum < len(t1outtext):
		out = out + t1intervalID[phoneNum] + t1xminLine[phoneNum] + t1xmaxLine[phoneNum]
		out = out + "\t\t\t\ttext = \"" + t1outtext[phoneNum] + "\"\r\n"
		phoneNum = phoneNum + 1
	
	out = out + midFile
	
	wordNum = 0
	while wordNum < len(t2text):
		out = out + t2intervalID[wordNum] + t2xminLine[wordNum] + t2xmaxLine[wordNum]
		out = out + "\t\t\t\ttext = \"" + t2text[wordNum] + "\"\r\n"
		wordNum = wordNum + 1
	
	open(outPath, "wb").write((out).encode('utf-8','replace'))
