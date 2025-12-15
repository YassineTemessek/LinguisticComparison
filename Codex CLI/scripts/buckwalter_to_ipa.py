"""
Simple Buckwalter -> IPA mapper for Arabic characters (Classical/Qur'anic focus).
This is a minimal table; extend as needed for dialectal vowels and shadda/hamza rules.
"""

BUCKWALTER_TO_IPA = {
    "b": "b",
    "t": "t",
    "v": "θ",
    "j": "d͡ʒ",
    "H": "ħ",
    "x": "x",
    "d": "d",
    "*": "ð",
    "r": "r",
    "z": "z",
    "s": "s",
    "$": "ʃ",
    "S": "sˤ",
    "D": "dˤ",
    "T": "tˤ",
    "Z": "ðˤ",
    "E": "ʕ",
    "g": "ɣ",
    "f": "f",
    "q": "q",
    "k": "k",
    "l": "l",
    "m": "m",
    "n": "n",
    "h": "h",
    "w": "w",
    "y": "j",
    "'": "ʔ",
    "A": "aː",
    "u": "u",
    "i": "i",
    "a": "a",
    "U": "uː",
    "I": "iː",
    "o": "o",
    "e": "e",
    "~": "ː",  # shadda marker (lengthen consonant)
}


def bw_to_ipa(text: str) -> str:
    out = []
    for ch in text:
        if ch in BUCKWALTER_TO_IPA:
            out.append(BUCKWALTER_TO_IPA[ch])
        else:
            out.append(ch)
    return "".join(out)


if __name__ == "__main__":
    samples = ["ktb", "kataba", "kaAtib", "Aml", "qwl", "s~ams"]
    for s in samples:
        print(s, "->", bw_to_ipa(s))
