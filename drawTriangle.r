# ===========================================================
# drawTriangle.r
# Rolando Coto-Solano. Victoria University of Wellington
# rolando.coto@vuw.ac.nz
# Last update: 20190219
#
# This code takes a file generated by the getPhonetics.praat 
# script (or the getDurationPitchFormants.praat of Mietta
# Lennes) and makes a vowel triangle using the phonR 
# package. These instructions are from the tutorial at:
# http://drammock.github.io/phonR/
#
# You need to select more than 1 vowel. If you don't,
# then the chart won't draw.
#
# You can learn more about charting vowels here:
# http://dan.mccloy.info/pubs/McCloy2012_phonR.pdf
# http://www.mattwinn.com/tools/HB95_2.html
# http://drammock.github.io/phonR/
# ===========================================================


# Load the necessary libraries
library(phonR)
library(ggplot2)


# Default args for testing
#fileName="C:\\Users\\Bender\\Desktop\\hello\\cimtesting\\cim-jane-extract.txt"
#inVowels = "a,e,i,o"
#decimalMarker = "."
#separatorMarker = "\t"
#f1min = -1
#f1max = -1
#f2min = -1
#f2max = -1
#vowelColName = "TextGridLabel"
#f1ColName = "F1_midpoint"
#f2ColName = "F2_midpoint"


# Read the arguments
args = commandArgs(trailingOnly = TRUE)
fileName = args[1]
inVowels = args[2]        # Vowels to be analyzed
decimalMarker = args[3]   # Symbol that the resultsFile uses to mark decimals (Arabic and Spanish Windows use commas; Hindi and English Windows use dots)
separatorMarker = args[4] # Separator between the columns (e.g. tabs, commas, semicolons)
f1min = as.integer(as.character(args[5])) # Minimum frequency for F1
f1max = as.integer(as.character(args[6])) # Maximum frequency for F1
f2min = as.integer(as.character(args[7])) # Minimum frequency for F2
f2max = as.integer(as.character(args[8])) # Maximum frequency for F2
vowelColName = args[9]    # Column that has the labels for the vowels (the default is for this to be "TextGridLabel")
f1ColName = args[10]      # Column that has the labels for F1 (the default is for this to be "F1_midpoint")
f2ColName = args[11]      # Column that has the labels for F2 (the default is for this to be "F2_midpoint")

# Verify the input you provided to the program
fileName
inVowels
decimalMarker
separatorMarker
f1min
f1max
f2min
f2max
vowelColName
f1ColName
f2ColName


# Read the file
if (separatorMarker == "\\t") { separatorMarker="\t" }
inputSounds = read.table(fileName, sep=separatorMarker[[1]], dec=decimalMarker, row.names=NULL, header=TRUE)


# Set the "undefined" pitch tracks to null
inputSounds[inputSounds=="--undefined--"] = ""


colnames(inputSounds)


# If the user requested a vowel column different from TextGridLabel, then rename that column
# as TextGridLabel, and rename the original TGL column as old_TGL (if it exists)
vowelColNameIndex = which(colnames(inputSounds)==vowelColName)
hasTGLIndex = which(colnames(inputSounds)=="TextGridLabel")
if (!vowelColName == "TextGridLabel") {
  if ( length(hasTGLIndex) > 0 ) { colnames(inputSounds)[hasTGLIndex] <- "old_TextGridLabel" }
  colnames(inputSounds)[vowelColNameIndex] <- "TextGridLabel"
}


# If the user requested an F1 column different from F1_midpoint, then rename that column
# as F1_midpoint, and rename the original F1 column as old_F1_midpoint (if it exists)
f1ColNameIndex = which(colnames(inputSounds)==f1ColName)
hasF1Index = which(colnames(inputSounds)=="F1_midpoint")
if (!f1ColName == "F1_midpoint") {
  if ( length(hasF1Index) > 0 ) { 
    colnames(inputSounds)[hasF1Index] <- "old_F1_midpoint"
  }
  colnames(inputSounds)[f1ColNameIndex] <- "F1_midpoint"
  if (f2ColName == "F1_midpoint") { f2ColName = "old_F1_midpoint" }
}

# If the user requested an F1 column different from F2_midpoint, then rename that column
# as F2_midpoint, and rename the original F2 column as old_F2_midpoint (if it exists)
f2ColNameIndex = which(colnames(inputSounds)==f2ColName)
hasF2Index = which(colnames(inputSounds)=="F2_midpoint")
if (!f2ColName == "F2_midpoint") {
  if ( length(hasF2Index) > 0 ) { colnames(inputSounds)[hasF2Index] <- "old_F2_midpoint" }
  colnames(inputSounds)[f2ColNameIndex] <- "F2_midpoint"
}


colnames(inputSounds)



# Filter the inputSounds dataframe so that it has only vowels.
# (This needs to be modified to the vowels in your dataframe)
vowelsToChart = unlist(strsplit(inVowels, "[,]"))
inputSounds = subset(inputSounds, TextGridLabel %in% vowelsToChart)



# Filter the sounds that are outside of the range chosen by the user
if ( !(f1min == -1 && f1max == -1 && f2min == -1 && f2max == -1)  ) {
  inputSounds = subset(inputSounds, F1_midpoint > f1min & F1_midpoint < f1max &  F2_midpoint > f2min & F2_midpoint < f2max)
}


# How many elements there are in inputSounds
nrow(inputSounds)

inputSounds


# Make sure that the columns for F1 and F2 and numbers
inputSounds = subset(inputSounds, !is.na(F1_midpoint) )
inputSounds = subset(inputSounds, !is.na(F2_midpoint) )
inputSounds$F1_midpoint = as.double(as.character(inputSounds$F1_midpoint))
inputSounds$F2_midpoint = as.double(as.character(inputSounds$F2_midpoint))



# Chart with all the vowels
with(inputSounds, 
     plotVowels(F1_midpoint, F2_midpoint, TextGridLabel, plot.tokens = TRUE, 
                plot.means = TRUE, pch.means = TextGridLabel, pch.tokens=TextGridLabel, 
                cex.means = 2, var.col.by = TextGridLabel, family = "Charis SIL", pretty = TRUE, output='pdf'))
file.rename(from="Rplot001.pdf",to="R-vowel-1.pdf")



# Chart with ellipses
with(inputSounds, plotVowels(F1_midpoint, F2_midpoint, TextGridLabel, group = TextGridLabel, plot.tokens = FALSE, plot.means = TRUE, 
                             pch.means = TextGridLabel, cex.means = 2, var.col.by = TextGridLabel, ellipse.fill = TRUE, pretty = TRUE, output="pdf"))
file.rename(from="Rplot001.pdf",to="R-vowel-2.pdf")