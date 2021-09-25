from difflib import SequenceMatcher

def string_similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()