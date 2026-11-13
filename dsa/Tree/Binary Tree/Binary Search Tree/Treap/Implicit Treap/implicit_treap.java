// ImplicitTreap is a special type of Treap that omits explicit search keys and instead uses subtree sizes to treat the tree as a dynamic array with O(log n) slicing/insertion.
public class ImplicitTreap extends Treap {
    public static class ImplicitNode extends TreapNode {
        public int subtreeSize; // Number of nodes in this subtree (determines implicit index)

        public ImplicitNode(int value) {
            super(value);
            this.subtreeSize = 1;
        }
    }

    protected int size(ImplicitNode node) {
        return (node == null) ? 0 : node.subtreeSize;
    }

    protected void updateSize(ImplicitNode node) {
        if (node != null) {
            node.subtreeSize = 1 + size((ImplicitNode) node.left) + size((ImplicitNode) node.right);
        }
    }
}