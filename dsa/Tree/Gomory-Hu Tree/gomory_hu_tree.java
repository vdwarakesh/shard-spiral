// GomoryHuTree is a special type of weighted Tree that compactly represents the
// Minimum s-t Cut values for all pairs of vertices in an undirected graph using V - 1 edges.
public class GomoryHuTree extends Tree {
    // Homogeneous arrays storing the tree parent and edge cut weight for each vertex.
    // Note: Can also be represented as an array of Edge objects.
    protected int[] parent;
    protected int[] edgeCutWeight;
    protected int numVertices;

    public GomoryHuTree(int numVertices) {
        super();
        this.numVertices = numVertices;
        this.parent = new int[numVertices];
        this.edgeCutWeight = new int[numVertices];
    }
}