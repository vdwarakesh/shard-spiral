# include <vector> include <cmath>

// HyperLogLog is a special type of ProbabilisticStructures that estimates set cardinalities within ~1% error inside small register arrays.
class HyperLogLog : public ProbabilisticStructures {
private:
    int bBits;
    int mRegisters;
    std::vector<uint8_t> registers;

public:
    HyperLogLog(int b = 10) : ProbabilisticStructures(0.01), bBits(b), mRegisters(1 << b), registers(mRegisters, 0) {}
};