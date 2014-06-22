
import glob
import sys
import csv

corpus_field = "corpus"
convo_field = "convo"
word_field = "word"
word_beg_field = "word.beg"
word_end_field = "word.end"
word_dur_field = "word.dur"
prec_word_field = "prec.word"
prec_word_beg_field = "prec.word.beg"
prec_word_end_field = "prec.word.end"
prec_word_dur_field = "prec.word.dur"
foll_word_beg_field = "foll.word.beg"
foll_word_end_field = "foll.word.end"
foll_word_dur_field = "foll.word.dur"
line_beg_field = "line.beg"
line_end_field = "line.end"
line_dur_field = "line.dur"
line_transcript_field = "line.transcript"
words_in_line_field = "words.in.line"
speaking_rate_field = "speaking.rate"
speaker_field = "speaker"
sex_field = "sex"
yob_field = "yob"
dialect_field = "dialect"
educ_field = "educ"

def search(files):
	"""Search transcripts."""
	results = []
        for file in files:
                trans = open(file,'U')
                for line in trans:
			line = line.split()
			for num, word in enumerate(line):
				if word == target:
					print line[num-1], word



                        if p.search(line):
                                 splitline = re.split('\s+',line)
                                 cs = splitline[0].split('-')[0][2:7]
                                 beg = str(splitline[1])
                                 end = str(splitline[2])
				 transline = re.split('\d\d\d\d\d\d',line)[2].split('\n')[0]
				 wordlist.append(str(word_safe + '_' + cs + ',' + beg + ',' + end + ',' + transline))
		trans.close()
        return wordlist

def get_pin(wordlist,cinfo):
	"""For each token, find the PIN of the speaker who uttered it."""
        pinlist = []
        for line in wordlist:
                if wordlist.index(line) >= sbeg and wordlist.index(line) <= send:
                        line = line.split(',')
                        wcs = line[0]
                        beg = line[1]
                        end = line[2]
			transline = line[3]
                        convo = line[0].split('_')[1][0:4]
                        speaker = line[0].split('_')[1][4]
                        for cline in cinfo:
                                cline = cline.split(',')
                                cinfo_convo = cline[0]
                                cinfo_speaker = cline[1].split('"')[1]
                                cinfo_pin = cline[2][1:5]
                                if cinfo_convo == convo and cinfo_speaker == speaker:
					pinlist.append(str(wcs + ',' + beg +
					',' + end + ',' + transline + ',' + cinfo_pin))
        pinlist.sort()
        return pinlist

def get_demo(pinlist,demo):
	"""For each token, get pertinent demographic info for the speaker who
	uttered it."""
        demolist = []
        for line in pinlist:
            line = line.split(',')
            wcs = line[0]
            beg = line[1]
            end = line[2]
	    transline = line[3]
            pin = line[4]
            for dline in demo:
                dline = dline.split(',')
                demo_pin = dline[0]
                sex = dline[3].split('"')[1][0]
                bday = dline[4][1:5]
                dial = dline[5].split('"')[1]
                educ = dline[6][1]
                if demo_pin == pin:
			demolist.append(str(wcs + ',' + beg + ',' + end + ',' +
			pin + ',' + sex + ',' + bday + ',' + dial + ',' + educ + ',' + transline))
        return demolist

def get_path(demolist,sounds):
	"""For each token, pull out the path to its sound file."""
	pathlist = []
	for line in demolist:
    		line = line.split(',')
    		wcs = line[0]
    		c = wcs.split('_')[1][0:4]
    		wordbeg = line[1]
    		wordend = line[2]
    		for sline in sounds:
        		if c in sline:
	            		pathlist.append(str(wcs + ',' + wordbeg + ',' +
				wordend + ',' + sline))
	return pathlist     

if __name__ == "__main__":
	#Input the word to be searched for.
	response = raw_input("Enter regex to search:\n")

	#Compile all line-by-line transcriptions
	files = glob.glob('/Users/laurel/Academic/Corpora/Switchboard/swb_ms98_transcriptions/*/*/*-trans.text')

	#Generate a safe version of the word if it has characters like an
	#apostrophe or a space that won't play nice with filenames.
	word_safe = raw_input("Enter safe version of word for filenames (no underscores!):\n")

	#Pull out all tokens of the desired word.
	p = re.compile(response)
	wordlist = get_word(files)

	#Print the number of files found and ask the user how many they would
	#like to analyze.
	answer = raw_input(str(len(wordlist))+" tokens found. How many would you like to extract?\n Enter 'all,' a number (followed by r to select at random, e.g. 500r),\n or 'q' if you would like to leave the program.\n")
	if answer == "all":
		sbeg = 0
		send = len(wordlist)-1
	elif answer == "q":
		sys.exit(0)
	elif "r" in answer:
        	answer = answer.split('r')[0]
	        sbeg = 0
        	send = float(answer)-1
	        random.shuffle(wordlist)
	else:
		sbeg = 0
		send = float(answer)-1

	#Make a folder where you'll store all output files for this word.
	if not os.path.exists(word_safe):
		os.makedirs(word_safe)

	#Open the table of conversations & PINs.
	g = open('/Users/laurel/Academic/Corpora/Switchboard/info/call_con_tab.csv','U')
	cinfo = g.readlines()
	g.close()

	#Find the PIN of the speaker who uttered each token.
	pinlist = get_pin(wordlist,cinfo)

	#Open the table of demographic info.
	h = open('/Users/laurel/Academic/Corpora/Switchboard/info/caller_tab.csv','U')
	demo = h.readlines()
	h.close()

	#Find the demographic info for the speaker who uttered each token.
	demolist = get_demo(pinlist,demo)

	#Compile all sound file paths.
	sounds = glob.glob('/Volumes/swb1_d1/data/*.sph')
			
	#Write the lines to the output file 'lines.csv' for coding and write the 
	#paths to the output file 'paths.csv' for Praat. 
	lines = open(word_safe + '/lines.csv','w')
	print >> lines, 'OBSERVED, STRUC, PREC_WORD, CONVO, SPEAKER, SEX, YOB, DIALECT, EDUC, LINE, NOTES, LINE_BEG, LINE_END'
	for line in demolist:
		line = line.split(',')
		wcs = line[0]
		beg = line[1]
		end = line[2]
		pin = line[3]
		sex = line[4]
		bday = line[5]
		dial = line[6]
		educ = line[7]
		transline = line[8]
		print >> lines, ',,,' + 'sw' + wcs.split('_')[1] + ',sw_' + pin + ',' + sex + ',' + bday + ',' + dial + ',' + educ + ',' + transline + ',,' + beg + ',' + end
	pathlist = get_path(demolist,sounds)
	lines.close()

	#Iterate over the list of paths and call Praat for each path in the 
	#list.
	for line in pathlist:
        	line = line.split(',')
	        wcs = line[0]
	       	begin = float(line[1])
		end = float(line[2])
		path = line[3]
		speaker = wcs[-1]
                if speaker == "A":
                        side = "sw0" + line[0].split('_')[1][:-1] + "_ch1"
# praat changed this :-[ side = "left"
                else:
                        side = "sw0" + line[0].split('_')[1][:-1] + "_ch2"
#                       side = "right"
		p = Popen('praat /Users/laurel/Dropbox/Dissertation/Empirical/Contraction/Scripts/switchboard-local.praat ' + wcs + ' ' + '/Users/laurel/'+word_safe + 	' ' + str(begin) + ' ' + str(end) + ' ' + path + ' ' + 
		side,shell=True, stdout=PIPE, stderr=PIPE)
		(out, err) = p.communicate()
		print out, err,
#When this gets too big, print every 100th: if n % 100 == 0:
		print wcs, "done"

	print 'All done!'
