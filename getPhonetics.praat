#------------------------------------------------------------------------------------------------------------------
# Get Pitch Formants for the normalized duration of a labeled TextGrid interval
# Rolando Coto-Solano, Victoria University of Wellington. rolando.coto@vuw.ac.nz
# Last update: December 2nd, 2018
#
# This script opens each sound file in a directory, looks for a corresponding TextGrid in (possibly) a different
# directory, and extracts f0, F1, and F2 from the midpoint(s) of any labelled interval(s) in the specified TextGrid
# tier. It also extracts the duration of the labelled interval(s). All these results are written to a tab-delimited
# text file.
#
# (The WAV and .TextGrid files cannot have spaces in their filenames. If they do, processing will fail).
#
# Based on getDurationPitchFormants.praat, written by Mietta Lennes (mietta.lennes@helsinki.fi)
# from the University of Helsinki and further modified by Dan Cloy (drmccloy@uw.edu)
# (v 4.7.2003 http://www.helsinki.fi/~lennes/praat-scripts/public/collect_formant_data_from_files.praat)
# Code for intensity from Shigeto Kawahara (http://user.keio.ac.jp/~kawahara/scripts/get_intensity_minmax.praat)
#------------------------------------------------------------------------------------------------------------------

form Get pitch formants and duration from labeled segments in files
	comment Directory of sound files. Be sure to include the final "/"
	text sound_directory C:\Users\Bender\Desktop\bb\
	sentence Sound_file_extension .wav
	comment Directory of TextGrid files. Be sure to include the final "/"
	text textGrid_directory C:\Users\Bender\Desktop\bb\
	sentence TextGrid_file_extension .TextGrid
	comment Full path of the resulting text file:
	text resultsfile C:\Users\Bender\Desktop\bb\resultsfile.txt
	comment Which tier do you want to analyze?
	integer Tier 1
	comment What is the decimal separator for your system?
	text decimalSeparator ,
	comment Formant analysis parameters
	positive Time_step 0.01
	integer Maximum_number_of_formants 5
	positive Maximum_formant_(Hz) 5500
	positive Window_length_(s) 0.025
	real Preemphasis_from_(Hz) 50
	comment Pitch analysis parameters
	positive Pitch_time_step 0.01
	positive Minimum_pitch_(Hz) 75
	positive Maximum_pitch_(Hz) 300
endform

# Make a listing of all the sound files in a directory:
Create Strings as file list... list 'sound_directory$'*'sound_file_extension$'
numberOfFiles = Get number of strings

# Check if the result file exists:
if fileReadable (resultsfile$)
	pause The file 'resultsfile$' already exists! Do you want to overwrite it?
	filedelete 'resultsfile$'
endif

# Create a header row for the result file: (remember to edit this if you add or change the analyses!)
header$ = "Filename	TextGridLabel	Word	PreviousLabel	FollowingLabel	start	end	duration	f0_0%point	f0_10%point	f0_20%point	f0_25%point	f0_30%point	f0_33%point	f0_40%point	f0_50%point	f0_60%point	f0_67%point	f0_70%point	f0_75%point	f0_80%point	f0_90%point	f0_100%point	F1_midpoint	F2_midpoint	F3_midpoint	intensity_midpoint'newline$'"
fileappend "'resultsfile$'" 'header$'

# Open each sound file in the directory:
for ifile to numberOfFiles
	filename$ = Get string... ifile
	Read from file... 'sound_directory$''filename$'

	# get the name of the sound object:
	soundname$ = selected$ ("Sound", 1)

	# Look for a TextGrid by the same name:
	gridfile$ = "'textGrid_directory$''soundname$''textGrid_file_extension$'"

	# if a TextGrid exists, open it and do the analysis:
	if fileReadable (gridfile$)
		Read from file... 'gridfile$'

		select Sound 'soundname$'
		To Formant (burg)... time_step maximum_number_of_formants maximum_formant window_length preemphasis_from

		select Sound 'soundname$'
		To Pitch... pitch_time_step minimum_pitch maximum_pitch

		select Sound 'soundname$'
		To Intensity... 100 0		

		select TextGrid 'soundname$'
		numberOfIntervals = Get number of intervals... tier
		numberOfIntervalsWordTier = Get number of intervals... 2

		# Pass through all intervals in the designated tier, and if they have a label, do the analysis:
		for interval to numberOfIntervals
			label$ = Get label of interval... tier interval
			if label$ <> ""

				# duration:
				start = Get starting point... tier interval
				end = Get end point... tier interval
				duration = end-start

				previousInterval = interval-1
				nextInterval = interval+1

				# previous label:
				if interval = 1
					previousLabel$ = "-"
				else
					previousLabel$ = Get label of interval... tier previousInterval
				endif

				# following label:
				if interval = numberOfIntervals
					followingLabel$ = "-"
				else
					followingLabel$ = Get label of interval... tier nextInterval
				endif

				# word that contains the sound label
				currentWord$ = ""
				for i from 1 to numberOfIntervalsWordTier
					tempWord$ = Get label of interval... 2 i
					tempStart = Get starting point... 2 i
					tempEnd = Get end point... 2 i
					if tempStart <= start && tempEnd >= end
						currentWord$ = tempWord$
					endif
				endfor

				tenpercent = start + (duration*0.1)
				twentypercent = start + (duration*0.2)
				twentyfivepercent = start + (duration*0.25)
				thirtypercent = start + (duration*0.3)
				thirtythreepercent = start + (duration*0.33)
				fortypercent = start + (duration*0.4)
				midpoint = (start + end) / 2
				sixtypercent = start + (duration*0.6)
				sixtysevenpercent = start + (duration*0.67)
				seventypercent = start + (duration*0.7)
				seventyfivepercent = start + (duration*0.75)
				eightypercent = start + (duration*0.8)
				ninetypercent = start + (duration*0.9)
				hundredpercent = start + duration

				# formants:
				select Formant 'soundname$'
				f1_50 = Get value at time... 1 midpoint Hertz Linear
				f2_50 = Get value at time... 2 midpoint Hertz Linear
				f3_50 = Get value at time... 3 midpoint Hertz Linear

				# intensity:
				select Intensity 'soundname$'
				intensity_50 = Get value at time... midpoint Cubic

				# pitch:
				select Pitch 'soundname$'
				f0_0 = Get value at time... start Hertz Linear
				f0_10 = Get value at time... tenpercent Hertz Linear
				f0_20 = Get value at time... twentypercent Hertz Linear
				f0_25 = Get value at time... twentyfivepercent Hertz Linear
				f0_30 = Get value at time... thirtypercent Hertz Linear
				f0_33 = Get value at time... thirtythreepercent Hertz Linear
				f0_40 = Get value at time... fortypercent Hertz Linear
				f0_50 = Get value at time... midpoint Hertz Linear
				f0_60 = Get value at time... sixtypercent Hertz Linear
				f0_67 = Get value at time... sixtysevenpercent Hertz Linear
				f0_70 = Get value at time... seventypercent Hertz Linear
				f0_75 = Get value at time... seventyfivepercent Hertz Linear
				f0_80 = Get value at time... eightypercent Hertz Linear
				f0_90 = Get value at time... ninetypercent Hertz Linear
				f0_100 = Get value at time... hundredpercent Hertz Linear

				# Save result to text file:
				resultline$ = "'soundname$'	'label$'	'currentWord$'	'previousLabel$'	'followingLabel$'	'start'	'end'	'duration'	'f0_0'	'f0_10'	'f0_20'	'f0_25'	'f0_30'	'f0_33'	'f0_40'	'f0_50'	'f0_60'	'f0_67'	'f0_70'	'f0_75'	'f0_80'	'f0_90'	'f0_100'	'f1_50'	'f2_50'	'f3_50'	'intensity_50''newline$'"
				resultline$ = replace$ (resultline$, ".", decimalSeparator$,0)
				fileappend "'resultsfile$'" 'resultline$'

				# select the TextGrid so we can iterate to the next interval:
				select TextGrid 'soundname$'
			endif
		endfor
		# Remove the TextGrid, Formant, and Pitch objects
		select TextGrid 'soundname$'
		plus Formant 'soundname$'
		plus Pitch 'soundname$'
		Remove
	endif
	# Remove the Sound object
	select Sound 'soundname$'
	Remove
	# and go on with the next sound file!
	select Strings list
endfor

# When everything is done, remove the list of sound file paths:
Remove
