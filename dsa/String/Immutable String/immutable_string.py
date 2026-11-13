# Immutable String is a special type of String whose contents cannot be modified in place.
# Python strings are immutable by design; any modification creates a new string object.
immutable_str = "Read-Only Text"
# immutable_str[0] = 'r'  # Raises TypeError: 'str' object does not support item assignment
modified_str = "r" + immutable_str[1:]  # Creates a brand new string in memory