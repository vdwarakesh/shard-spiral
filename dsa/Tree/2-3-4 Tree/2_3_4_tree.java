// TwoThreeFourTree (2-3-4 Tree) is a special type of BTree of order 4 where each node holds up to 3 keys and 4 children. It is structurally isomorphic to a Red-Black Tree.
public class TwoThreeFourTree extends BTree {
    public static final int MAX_KEYS = 3;     // Up to 3 keys per 4-node
    public static final int MAX_CHILDREN = 4; // max_degree_4 multi-way branching

    public TwoThreeFourTree() {
        // Order-4 B-Tree (minimum degree t = 2 gives 2t - 1 = 3 max keys and 2t = 4 max children)
        super(2);
    }
}