# include <vector> include <unordered_map> include <string>

// SuffixAutomaton is a special type of String state machine (DAWG) that encodes all substrings of a text inside at most 2n - 1 states.
class SuffixAutomaton {
public:
    struct State {
        int length;
        int link;
        std::unordered_map<char, int> next;
        State(int len = 0, int lk = -1) : length(len), link(lk) {}
    };

protected:
    std::vector<State> st;
    int last;

public:
    SuffixAutomaton(const std::string& text = "") {
        st.emplace_back(0, -1);
        last = 0;
    }
};