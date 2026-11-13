# Suffix Trie is a special type of Trie that stores every possible suffix of a single string.
# This turns any substring search into a simple prefix walk starting from the root.
class SuffixTrie(Trie):
    def __init__(self, text=""):
        super().__init__()
        # Insert every suffix of the text (e.g., "BANANA", "ANANA", "NANA", ...) into the Trie
        for i in range(len(text)):
            self.insert(text[i:])