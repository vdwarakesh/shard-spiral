# Wavelet Tree is a special type of Binary Tree that recursively partitions an array by value range (alphabet) rather than position, storing a compact 0/1 bitvector at each node to track whether elements went left (<= mid) or right (> mid).
class WaveletTreeNode(BinaryTreeNode):
    def __init__(self, low_val, high_val):
        super().__init__(None)
        self.low_val = low_val      # Minimum value in this node's alphabet range
        self.high_val = high_val    # Maximum value in this node's alphabet range
        self.prefix_zeros = [0]     # Rank lookup table counting elements sent to left child


class WaveletTree(BinaryTree):
    def __init__(self, arr, low_val, high_val):
        super().__init__()
        self.root = self._build(arr, low_val, high_val)

    def _build(self, arr, low, high):
        node = WaveletTreeNode(low, high)
        if low == high or not arr:
            return node
        mid = (low + high) // 2
        left_arr, right_arr = [], []
        for x in arr:
            if x <= mid:
                left_arr.append(x)
                node.prefix_zeros.append(node.prefix_zeros[-1] + 1)
            else:
                right_arr.append(x)
                node.prefix_zeros.append(node.prefix_zeros[-1])
        node.left = self._build(left_arr, low, mid)
        node.right = self._build(right_arr, mid + 1, high)
        return node