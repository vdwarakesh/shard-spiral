# Mutable String is a special type of String whose characters can be edited, overwritten, or appended in place using a bytearray or list buffer.
class MutableString:
    def __init__(self, initial_text=""):
        # Store characters in a mutable bytearray or list of chars
        self.buffer = bytearray(initial_text, "utf-8")

    def set_char(self, index, char_code):
        # Mutate character in place in O(1) time
        self.buffer[index] = char_code

    def append(self, text):
        self.buffer.extend(text.encode("utf-8"))

    def to_string(self):
        return self.buffer.decode("utf-8")