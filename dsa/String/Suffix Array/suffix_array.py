# Suffix Array is a special type of String data structure consisting of a sorted array of integers representing the starting indices of all suffixes of a text.
class SuffixArray:
    def __init__(self, text):
        self.text = text
        # Generate all suffixes paired with their starting index and sort lexicographically
        suffixes = [(text[i:], i) for i in range(len(text))]
        suffixes.sort(key=lambda x: x[0])
        # Suffix array stores only the sorted starting index integers
        self.sa = [idx for _, idx in suffixes]