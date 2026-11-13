// TwoThreeTree (2-3 Tree) is a special type of BTree where every internal node holds
// 1 or 2 keys and branches into 2 or 3 children, staying perfectly height-balanced.
public class TwoThreeTree extends BTree {
    public static final int MAX_KEYS = 2;     // 2-node (1 key) or 3-node (2 keys)
    public static final int MAX_CHILDREN = 3; // max_degree_3 multi-way branching

    public TwoThreeTree() {
        // Initialize B-Tree with max 3 children per node
        super(2);
    }
}