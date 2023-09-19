
def chord_to_harmony(chord, key, pitch):

    import midi
    
    if "C" in str(key):
        offset = 0
    elif "D" in str(key):
        offset = 2
    elif "E" in str(key):
        offset = 4
    elif "F" in str(key):
        offset = 5
    elif "G" in str(key):
        offset = -5
    elif "A" in str(key):
        offset = -3
    elif "B" in str(key):
        offset = -1

    if "iii" in str(chord):
        root = 4
    elif "ii" in str(chord):
        root = 2
    elif "iv" in str(chord):
        root = 5
    elif "vii" in str(chord):
        root = 11
    elif "vi" in str(chord):
        root = 9
    elif "V" in str(chord):
        root = 7
    elif "I" in str(chord):
        root = 0

    root = root + offset + pitch
    third = root + 4
    fifth = root + 7
    #print root
    return root, third, fifth
