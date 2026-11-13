import java.util.ArrayList;
import java.util.List;

// DominatorTree is a special type of Tree where each node's parent is its Immediate
// Dominator (idom)-the unique closest node that dominates it on all paths from the start node.
public class DominatorTree extends Tree {
    // Homogeneous integer array mapping each vertex v to its Immediate Dominator idom[v]
    protected int[] idom;
    protected List<Integer>[] domChildren;
    protected int entryRoot;

    @SuppressWarnings("unchecked")
    public DominatorTree(int numVertices, int entryRoot) {
        super();
        this.entryRoot = entryRoot;
        this.idom = new int[numVertices];
        this.domChildren = new ArrayList[numVertices];
        for (int i = 0; i < numVertices; i++) {
            this.idom[i] = -1;
            this.domChildren[i] = new ArrayList<>();
        }
        this.idom[entryRoot] = entryRoot;
    }
}