# Suffix Automaton is a special type of String structure that compresses all substrings of a text into a minimal directed acyclic word graph (DAWG) of at most 2n - 1 states.
class SAMState:
    def __init__(self, length=0, link=-1):
        self.length = length       # Longest substring length accepted by this state
        self.link = link           # Suffix link to parent state
        self.next = {}             # Character transition map -> state index


class SuffixAutomaton:
    def __init__(self, text=""):
        self.st = [SAMState(0, -1)]  # List of states
        self.last = 0                # Index of the state representing the whole prefix
        for ch in text:
            self.extend(ch)

    def extend(self, c):
        cur = len(self.st)
        self.st.append(SAMState(self.st[self.last].length + 1, -1))
        p = self.last
        while p != -1 and c not in self.st[p].next:
            self.st[p].next[c] = cur
            p = self.st[p].link
        # (Continuation of state transitions omitted for brevity; structure instantiated)
        self.last = cur