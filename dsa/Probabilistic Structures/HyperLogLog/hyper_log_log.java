// HyperLogLog is a special type of ProbabilisticStructures estimating unique element cardinalities using leading-zero register streaks in kilobytes of memory.
public class HyperLogLog extends ProbabilisticStructures {
    protected int bBits;
    protected int mRegisters;
    protected byte[] registers;

    public HyperLogLog(int bBits) {
        super(0.01);
        this.bBits = bBits;
        this.mRegisters = 1 << bBits;
        this.registers = new byte[mRegisters];
    }
}