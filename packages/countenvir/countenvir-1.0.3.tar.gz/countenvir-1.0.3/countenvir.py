""" This is the countletters module which simply reads txt files and counts the occurrence of all 26 latin letters."""

def countletters(inputfile, outputfile, percent=1):
	""" This function counts the occurrances of every of the 26 latin letters.
	Mandatory:
	As first  argument you need to give the filename to read from.
	The second argument is the filename to be written to."""
	letters = [['a', 0], ['b', 0], ['c', 0], ['d', 0], ['e', 0], ['f', 0],
		   ['g', 0], ['h', 0], ['i', 0], ['j', 0], ['k', 0], ['l', 0],
		   ['m', 0], ['n', 0], ['o', 0], ['p', 0], ['q', 0], ['r', 0],
		   ['s', 0], ['t', 0], ['u', 0], ['v', 0], ['w', 0], ['x', 0], ['y', 0], ['z', 0]]

	alltogether = 0

	try:
		#print('test')
		#print (inputfile)
		#print (outputfile)
		with open(inputfile, 'r') as filetocount, open(outputfile, 'w') as resultfile:
			# going through the file and counting
			for each_line in filetocount:
				for each_character in each_line:
					for theletter in letters:
						if str.lower(theletter[0]) == each_character:
							theletter[1] += 1
							alltogether += 1

			# going through the result matrix and write it to disk
			print('LETTER;ABSOLUTE FREQUENCY;RELATIVE FREQUENCY IN %', file=resultfile)
			for each_element in letters:
				print(each_element[0] + '; ' + str(each_element[1]) + '; ' + str((each_element[1]/alltogether)*100), file=resultfile)
			print('ALL; ' + str(alltogether) + '; 100', file=resultfile) 

	except IOError as err:
		print('Error: ' + str(err))

	finally:
		print('done')
