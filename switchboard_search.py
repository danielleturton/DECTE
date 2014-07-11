#wordaligned = "/Volumes/LEL_corpora/PDE/Switchboard/swb_ms98_transcriptions/20/2007/*-word.text"
#wordaligned = "/Volumes/LEL_corpora/PDE/Switchboard/swb_ms98_transcriptions/*/*/*-word.text"
#pintable = "/Volumes/LEL_corpora/PDE/Switchboard/info/call_con_tab.csv"
#demotable = "/Volumes/LEL_corpora/PDE/Switchboard/info/caller_tab.csv"
#dictpath = '/Users/laurelmackenzie/Documents/Corpora/cmudict.0.7a.txt'
#target = "he"
#outpath = "test.csv"

import glob
import sys
import csv
import re
import argparse

def search(wordaligned, pintable, demotable, target, compare, avoid):
	"""Search word-aligned transcripts for target word; return various social & linguistic factors."""
	hits = []
	pins = csv.DictReader(open(pintable), fieldnames = ["convo", "side", "PIN", "", "", "", "", ""])
	demo = csv.DictReader(open(demotable), fieldnames = ["PIN", "", "", "sex", "yob", "dialect", "educ"])
        for trans in wordaligned:
                o = open(trans,'U')
		convo = trans.split('/')[-1].split('-')[0][2:6]
		side = trans.split('/')[-1].split('-')[0][6]
		for row in pins: #get PIN of speaker
			if row["convo"] == convo and row["side"] == str(" " + '"' + side + '"'):
				PIN = row["PIN"].strip()
		for row in demo: #get demographic info of speaker
			if row["PIN"] == PIN:
				sex, yob, dialect, educ = row["sex"].strip().strip('"')[0], row["yob"].strip(), row["dialect"].strip().strip('"'), row["educ"].strip()
		lines = [x for x in o if "[silence]" not in x] #removes [silence]s, which are not words
                for num, line in enumerate(lines):
			line = line.split()
			word = line[-1]
			if target in word:
				try:
					foll_line = lines[num+1].split()
					foll_word, foll_word_beg, foll_word_end = foll_line[3], foll_line[1], foll_line[2]
					foll_pause = float(line[2]) - float(foll_word_beg)
					if foll_pause > 0:
						foll_word = "pause"
						foll_word_end = foll_word_beg
						foll_word_beg = line[2]
						foll_word_dur = foll_pause
					else:
						foll_word_dur = float(foll_word_end) - float(foll_word_beg)
			except IndexError:
				foll_word, foll_word_beg, foll_word_end, foll_word_dur = "NA", "NA", "NA", "NA"				

			if "'" in target:
				if target in word:
					prec_word, prec_word_beg, prec_word_end = line[-1].split("'")[0], line[1], line[2]
					prec_word_dur = float(prec_word_end) - float(prec_word_beg)			
			else:
				if word == target:
					try:
						prec_line = lines[num-1].split()
						prec_word, prec_word_beg, prec_word_end = prec_line[3], prec_line[1], prec_line[2]
						prec_pause = float(line[1]) - float(prec_word_end)
						if prec_pause > 0: #because sometimes multiple silences precede and we want to combine them
							prec_word = "[pause]"
							prec_word_beg = prec_word_end
							prec_word_end = line[1]
							prec_word_dur = prec_pause
						else:
							prec_word_dur = float(prec_word_end) - float(prec_word_beg)
					except IndexError:
						prec_word, prec_word_beg, prec_word_end, prec_word_dur = "NA", "NA", "NA", "NA"
			if args.avoid == "pronouns": #check these for case before running this on Fisher
				pronouns = frozenset(["i", "you", "he", "she", "it", "we", "they", "which", "who", "what", "how", "why", "where", "when", "that", "this", "there", "everyone", "everything", "everybody", "someone", "something", "somebody", "anyone", "anything", "anybody", "no one", "nothing", "nobody"])
				if prec_word in pronouns:
					continue

			p = open(trans.replace('word', 'trans'))
			linealigned = [x for x in p]
			p.close()
			for l in linealigned:
				if float(l.split()[1]) <= float(line[1]) and float(line[2]) <= float(l.split()[2]):
					if args.compare:
						c = csv.DictReader(open(args.compare, 'rUb'))
						coded = []
						for item in c:
							coded.append(item["line.transcript"])
						if ' '.join(re.split('\s+', l.strip())[3:]) in coded:
							continue						
					if "'" in target:
						hits.append([PIN, sex, dialect, yob, educ, convo + side, word, "NA", "NA", "NA", prec_word, prec_word_beg, prec_word_end, prec_word_dur, foll_word, foll_word_beg, foll_word_end, foll_word_dur, ' '.join(re.split('\s+', l.strip())[3:]), re.split('\s+', l.strip())[1], re.split('\s+', l.strip())[2]])
					else:
						hits.append([PIN, sex, dialect, yob, educ, convo + side, word, line[1], line[2], float(line[2]) - float(line[1]), prec_word, prec_word_beg, prec_word_end, prec_word_dur, foll_word, foll_word_beg, foll_word_end, foll_word_dur, ' '.join(re.split('\s+', l.strip())[3:]), re.split('\s+', l.strip())[1], re.split('\s+', l.strip())[2]])
		o.close()
        return hits

def segment_lookup(word, position, dict):
    """Open CMUdict, look up word, return relevant fields. If a word can't be found, return 'unknown'. When a line has multiple entries, this will take the first one. Not a perfect solution in cases of variation or homonymy (e.g. REcord/reCORD) but I don't know how else to do it."""
    seg, stress = "unknown",  "unknown"
    for line in dict:
        item = line[0]
	trans = line[1].split()
	if item == word.upper():
            if position == "prec":
                trans.reverse() #reverse the transcription bc we want to know what's at the end of it
	    seg = re.split("[0-9]", trans[0])[0] #get the phoneme at index 0
	    for phone in trans:
		if stress == "unknown" and re.search("[0-9]", phone): #find the leftmost phoneme with a number on it (i.e. the leftmost vowel)
		    stress = re.split("[A-Z]", phone)[-1] #and get its stress
    stresses = {"0" : "unstressed", "1": "primary", "2": "secondary", "unknown": "unknown"}
    stress = stresses[str(stress)]
    return (stress, seg)


def main(wordaligned, pintable, demotable, dictpath, target, outpath, compare, avoid):

	hits = search(glob.glob(wordaligned), pintable, demotable, target, compare, avoid)

	d = open(dictpath, 'rUb')
	dict = [re.split("\s{2}", line) for line in d.readlines() if ";" not in line]

	out = open(outpath, 'wt')
	writer = csv.writer(out)
	writer.writerow(["corpus", "convo", "word", "word.beg", "word.end", "word.dur", "prec.word", "prec.word.beg", "prec.word.end", "prec.word.dur", "prec.stress", "prec.seg", "foll.word", "foll.word.beg", "foll.word.end", "foll.word.dur", "foll.stress", "foll.seg", "line.beg", "line.end", "line.dur", "line.transcript", "words.in.line", "speaking.rate", "speaker", "sex", "yob", "dialect", "educ"])
	for item in hits:
		if item[9] != "[pause]":
			prec_stress, prec_seg = segment_lookup(item[9], "prec", dict)
		else:
			prec_stress, prec_seg = "NA", "NA"
		if item[13] != "[pause]":
			foll_stress, foll_seg = segment_lookup(item[13], "foll", dict)
		else:
			foll_stress, foll_seg = "NA", "NA"
		words_in_line = item[17].count(" ") + 1 #note that this is dumb: it counts [laughter], [vocalized-noise], etc. as words
		writer.writerow(["Switchboard", item[5], item[6], item[7], item[8], item[9], item[10], item[11], item[12], item[13], prec_stress, prec_seg, item[14], item[15], item[16], item[17], foll_stress, foll_seg, item[19], item[20], float(item[20]) - float(item[19]), item[18], words_in_line, words_in_line/(float(item[20]) - float(item[19])), item[0], item[1], item[3], item[2], item[4]])
	out.close()

if __name__ == "__main__":
    try:
	parser = argparse.ArgumentParser()
	parser.add_argument("wordaligned", help = "path to word-aligned transcripts")
	parser.add_argument("pintable", help = "path to table of pins")
	parser.add_argument("demotable", help = "path to table of demographic info")
	parser.add_argument("dictpath", help = "path to CMU dictionary")
	parser.add_argument("target", help = "word to search for")
	parser.add_argument("outpath", help = "path to output file")
	parser.add_argument("-c", "--compare", help = "compare to file of existing coded tokens?")
	parser.add_argument("-a", "--avoid", help = "avoid a particular set of preceding words?")
	args = parser.parse_args()
	main(args.wordaligned, args.pintable, args.demotable, args.dictpath, args.target, args.outpath, args.compare, args.avoid)
	#        main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])
    except IndexError:
        print >> sys.stderr, "Usage: switchboard_search.py wordaligned_path pintable demotable dictpath target_word outpath"
        sys.exit(1)
