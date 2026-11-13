import java.util.HashMap;
import java.util.Map;
import java.util.ArrayList;
import java.util.List;

// SuffixAutomaton is a special type of String structure forming a minimal finite state machine that recognizes every substring of a text in linear time.
public class SuffixAutomaton {
    public static class State {
        public int length;
        public int link;
        public Map<Character, Integer> transitions;

        public State(int length, int link) {
            this.length = length;
            this.link = link;
            this.transitions = new HashMap<>();
        }
    }

    protected List<State> states;
    protected int lastState;

    public SuffixAutomaton(String text) {
        this.states = new ArrayList<>();
        this.states.add(new State(0, -1)); // Initial state 0
        this.lastState = 0;
    }
}