// OrderStatisticTree is a special type of BinarySearchTree where every node stores its subtree size, enabling O(log n) k-th order statistic (select) and rank lookups.
public class OrderStatisticTree extends BinarySearchTree {
    public static class OSNode extends BinaryNode {
        public int size; // Count of nodes in this subtree

        public OSNode(int key) {
            super(key);
            this.size = 1;
        }
    }

    protected int getSize(OSNode node) {
        return (node == null) ? 0 : node.size;
    }
}