def linear_search(arr, target, start_index=0, end_index=None):
    if end_index is None:
        end_index = len(arr) - 1
    for i in range(start_index, end_index + 1):
        if arr[i] == target:
            return i
    return -1