// WaveletTree is a special type of BinaryTree that recursively splits elements by their value range [low, high] and stores a prefix rank array at each node for quantile queries.
public class WaveletTree extends BinaryTree {
    public static class WaveletNode extends BinaryNode {
        public int lowVal;
        public int highVal;
        // Homogeneous array recording cumulative count of elements <= mid up to index i
        public int[] prefixZeros;

        public WaveletNode(int lowVal, int highVal, int length) {
            super(0);
            this.lowVal = lowVal;
            this.highVal = highVal;
            this.prefixZeros = new int[length + 1];
        }
    }

    public WaveletTree() {
        super();
    }
}