// MergeSortTree is a special type of SegmentTree where every node stores a fully sorted array of all elements in its interval [L, R].
public class MergeSortTree extends SegmentTree {
    // 2D array: sortedTree[node] holds a sorted int[] of elements in that segment.
    // Note: Can also use List<Integer>[] or arrays of other Comparable types.
    protected int[][] sortedTree;

    public MergeSortTree(int[] arr) {
        super(new int[0]);
        this.n = arr.length;
        this.sortedTree = new int[4 * n][];
    }
}