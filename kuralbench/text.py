# Vendored from thirukkural tkcore/signature.py at commit f5e2b6753052d098b745b6857bfd3378071e6d65 (CC0-1.0):
# constants, nfc, compare_key and aksharas, copied unchanged; only imports differ.
import re
import unicodedata

VOWELS = "அஆஇஈஉஊஎஏஐஒஓஔ"
SIGN = {"அ": "", "ஆ": "ா", "இ": "ி", "ஈ": "ீ", "உ": "ு", "ஊ": "ூ", "எ": "ெ", "ஏ": "ே", "ஐ": "ை", "ஒ": "ொ", "ஓ": "ோ", "ஔ": "ௌ"}
SIGN_TO_VOWEL = {v: k for k, v in SIGN.items() if v}
CONS = set("கஙசஞடணதநபமயரலவழளறனஜஷஸஹஶ")
PULLI = "்"
AU_SEQ = re.compile("ெள(?![ா-்ௗ])")


def nfc(s):
    return unicodedata.normalize("NFC", s)


def compare_key(text):
    """Spacing-, punctuation- and joining-insensitive key: NFC, கௌ written as U+0BCC, Tamil letters only, and a pulli
    consonant followed by a vowel letter written as consonant + vowel sign (how the prints join words)."""
    t = AU_SEQ.sub("ௌ", nfc(text))
    t = "".join(c for c in t if 0x0B80 <= ord(c) <= 0x0BFF)
    return re.sub("்([அஆஇஈஉஊஎஏஐஒஓஔ])", lambda m: SIGN[m.group(1)], t)


def aksharas(word):
    """Split into letters: (consonant or None, vowel or None) pairs; a pulli consonant has vowel None."""
    w, out, i = nfc(word), [], 0
    while i < len(w):
        c = w[i]
        if c in CONS:
            nxt = w[i + 1] if i + 1 < len(w) else ""
            if nxt == PULLI:
                out.append((c, None)); i += 2
            elif nxt in SIGN_TO_VOWEL:
                out.append((c, SIGN_TO_VOWEL[nxt])); i += 2
            else:
                out.append((c, "அ")); i += 1
        elif c in VOWELS:
            out.append((None, c)); i += 1
        elif c == "ஃ":
            out.append(("ஃ", None)); i += 1
        else:
            i += 1
    return out
