# usage = python format_DECTE.py infile outfile
## This will need to be changed to take a folder of XML files

import xml.etree.ElementTree as ET
import argparse
import sys

replacements = {"<pause/>": "", "<unclear/>": "(())", "<vocal><desc>laughter</desc></vocal>": "{LG}", "<incident><desc>interruption</desc></incident>": ""}

def clean_markup(line):
    """Convert/delete DECTE-style markup to make transcript FAVE-friendly"""
    for markup, replacement in replacements.iteritems():
        line = line.replace(markup, replacement) # replace markup according to list of replacements above
        line = line.replace("  ", " ") # get rid of double spaces that result
    return line

def make_subset(speaker, holding):
    """Make by-speaker subsets for each 20-second time chunk"""
    subset = [item for item in holding if item[0] == speaker] #create a subset for this speaker
    return subset

def make_increment(subset):
    """Create an increment based on how many lines a speaker utters in a 20-second time chunk"""
    if len(subset) > 0: # provided that the speaker spoke in this chunk
        increment = 20.0/len(subset) # make an increment
        new_beg = subset[0][2] # begin time of first item in list
    else:
        increment = 0
        new_beg = 0
    return new_beg, increment

def advance_subset(subset, new_beg, increment):
    """Advance the timestamps withina 20-second time chunk by the increment so they fill the time chunk"""
    advanced_subset = []
    if len(subset) > 0:
        for item in subset:
            new_end = new_beg + increment
            advanced_subset.append([item[0], item[1], new_beg, new_end, item[4]])
            new_beg = new_end
    else:
        advanced_subset = []
    return advanced_subset

def main(infile, outfile):

    f = open(infile)
    input = f.readlines()
    f.close()

    cleaned_lines = [clean_markup(line) for line in input]

    cleaned_transcript = ''.join(cleaned_lines)

    root = ET.fromstring(cleaned_transcript)
    ortho_tag = root.attrib.values()[0] + "necteortho" # this tag marks the start of the orthographic transcript in the tree

    speakers = [person.attrib.values()[0] for person in root.iter("person")] # list conversation participants

    interim = [] # contains lines of orthographic transcript (only), pre-formatting

    for text in root.iter("text"): # find all the text tags
        if text.attrib and text.attrib.values()[0] == ortho_tag: # when you reach the ortho trans text tag
            body = text[0] # go down a level
            timestamp = 0.0
            for u in body.findall("u"): # find all the u (speech) tags within body and pull out the text
                speaker = u.attrib.values()[0][1:]
                if u.text != " ":
                    interim.append([speaker, speaker, timestamp, timestamp+20, u.text.strip()])
                for child in u:
                    timestamp = float(child.attrib.values()[0][-4:])
                    interim.append([speaker, speaker, timestamp, timestamp+20, child.tail.strip()])

    holding = [] # hold transcript lines from each time chunk for processing

    # beginning & end of first 20-second time chunk
    beg = interim[0][2]
    end = interim[0][3]

    new = [] # put formatted transcript lines here


    for line in interim:
        if line[2] == beg and line[3] == end: # while speech is within a given time chunk
            holding.append(line) # add speech to holding pen
        else:
            for speaker in speakers: # once you move on to the next time chunk, process each speaker's lines
                subset = make_subset(speaker, holding)
                new_beg, increment = make_increment(subset)
                advanced_subset = advance_subset(subset, new_beg, increment)
                for item in advanced_subset:
                    new.append(item)
            beg = line[2] # and then start adding the current time chunk to the holding pen
            end = line[3]
            holding = []
            holding.append(line)

    for speaker in speakers: # finally, process the last time chunk
        subset = make_subset(speaker, holding)
        new_beg, increment = make_increment(subset)
        advanced_subset = advance_subset(subset, new_beg, increment)
        for item in advanced_subset:
            new.append(item)

    with open(outfile, 'wb') as o:
        for item in new:
            print >> o, "\t".join([str(i) for i in item])

if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("infile", help = "path to input XML file")
        parser.add_argument("outfile", help = "path to output formatted .txt file")
        args = parser.parse_args()
        main(args.infile, args.outfile)
    except IndexError:
        print >> sys.stderr, "Usage: format_DECTE.py infile outfile"
        sys.exit(1)

