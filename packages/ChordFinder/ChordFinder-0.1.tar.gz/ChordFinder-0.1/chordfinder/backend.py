
import re

chr_scale = ['A','A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#']


#Return an iterable object from parse_notes
#Add unicode sharp and flat symbols later, maybe allow double sharps and flats
#optimize parse notes? only try iterating if length > 1? iterate from pos 1 onward only?

def parse_notes(notes):
    """ Parses a string, extracts valid musical notes, and converts them to sharp notation

    It is much simpler for this program to handle only sharp notation. This function extracts any
    valid note using regular expressions (letters A through G, lowercase or uppercase, followed by
    anywhere from 0 to 2 sharps or flats). It then converts them into sharp notation by finding their
    place on the chromatic scale, and incrementing or decrementing this scale index when a sharp or
    flat symbol is encountered. Because the chromatic scale list contains only naturals and sharps,
    we are guaranteed such output from this function.

    Args:
        A string of user input, supposedly containing musical notes optionally with sharp or flat signs (up to 2)
    Returns:
        A list of valid sharp-notation notes

    """
    raw_list = re.compile("[A-Ga-g][#b]{0,2}").findall(notes) #Compile a regular expression and use it to find all occurrences in the user input
    parsed_list = [] #The final sanitized list of notes in sharp notation will be stored here
    for note in raw_list:
        note_name = note[0] #The first character of the string is the name of the note (e.g. as A is to "A#")
        chr_note_pos = chr_scale.index(note_name.upper()) #Find the chromatic index of this note name
        for char in note:
            if char == "#" : chr_note_pos += 1  #If we encounter a sharp or a flat, increment or decrement the chromatic index
            if char == "b" : chr_note_pos -= 1
        final_chr_note = chr_scale[(chr_note_pos + 12) % 12]    #The sharp note equivalent to the input can now be found at chr_note_pos
                                                                #We use the modolus operator to wrap around the scale if needed (e.g. G## or Ab)
        parsed_list.append(final_chr_note)      #Append each sharp or natural note to a list and return it when we have parsed all input
    return parsed_list



#Should the chord intervals be contained in a tuple? That way, they could be the key rather than the value
chord_name_dict = {"Major": [0,4,7], "Minor": [0,3,7],
                   "Major7" : [0, 4, 7, 11],"Minor7": [0,3,7,10],
                   "Dominant7":[0,4,7,10], "Major6" : [0, 3, 7, 10],"Minor6": [0, 3, 7, 8],
                   "Sus2": [0,2,7], "Sus4": [0,5,7],
                   "Add2": [0,2,4,7], "Add9": [0,4,5,7]}




def find_chords(notes):
    """ Returns a list of chord names that apply to the notes given

    Breaks down the given notes into a relative numerical pattern and attempts to match this
    with a library of known chord types. The result is returned as a string with the tonic
    note, followed by the chord type

    Args:
        A list of valid notes in sharp notation

    Returns:
        A list of containing a human-readable string for each chord found

    """
    notes = set(parse_notes(notes))
    chord_names = []
    for tonic in notes:#Each iteration, we assume a different note is a the tonic note
        pattern = []
        for note in notes: #Iterate through each other note and compare them to the tonic

            interval = ((chr_scale.index(note) - chr_scale.index(tonic)) + 12) %12

            pattern.append(interval)

        #pattern = list(set(pattern)) #Remove duplicate intervals
        pattern.sort() #Sort the list of interval

        for name, match_pattern in chord_name_dict.items():
            if pattern == match_pattern:
                chord_names.append(str(tonic) + " " + str(name))
    return chord_names




