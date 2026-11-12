# python/array.py

class VisualArray(list):
    """Array proxy that records bar inspections, swaps/mutations, and return matches.
    Only this specific object instance is visualized on the canvas."""
    def __init__(self, raw_list):
        super().__init__(raw_list)
        self.active_index = -1
        self.found_index = -1
        self.checked_indices = []
        self._step_accessed = []

    def on_step_start(self):
        self._step_accessed.clear()

    def _record_access(self, idx):
        if not isinstance(idx, int):
            return
        n = len(self)
        norm_idx = idx if idx >= 0 else n + idx
        if 0 <= norm_idx < n:
            if self.active_index != -1 and self.active_index != norm_idx:
                if self.active_index not in self.checked_indices:
                    self.checked_indices.append(self.active_index)
            self.active_index = norm_idx
            if norm_idx not in self._step_accessed:
                self._step_accessed.append(norm_idx)

    def __getitem__(self, idx):
        if isinstance(idx, int):
            self._record_access(idx)
        elif isinstance(idx, slice):
            start, stop, step = idx.indices(len(self))
            for i in range(start, stop, step):
                self._record_access(i)
        return super().__getitem__(idx)

    def __setitem__(self, idx, val):
        if isinstance(idx, int):
            self._record_access(idx)
        super().__setitem__(idx, val)

    def insert(self, idx, val):
        super().insert(idx, val)
        self._record_access(idx)

    def append(self, val):
        super().append(val)
        self._record_access(len(self) - 1)

    def pop(self, idx=-1):
        if len(self) > 0:
            norm_idx = idx if idx >= 0 else len(self) + idx
            self._record_access(norm_idx)
        return super().pop(idx)

    def on_line_fallback(self, loop_target_vars, frame_locals, is_while_line=False):
        if not self._step_accessed:
            for val in loop_target_vars:
                if isinstance(val, int) and not isinstance(val, bool) and 0 <= val < len(self):
                    self._record_access(val)
                    break

    def enhance_state_vars(self, state_vars, frame_locals, first_param_name):
        if 0 <= self.active_index < len(self):
            state_vars[f"{first_param_name}[{self.active_index}]"] = _serialize(super().__getitem__(self.active_index))

    def on_return(self, ret_val):
        if isinstance(ret_val, int) and not isinstance(ret_val, bool) and 0 <= ret_val < len(self):
            self.found_index = ret_val
            self.active_index = ret_val
        elif self.active_index != -1:
            if self.active_index not in self.checked_indices:
                self.checked_indices.append(self.active_index)
            self.active_index = -1
        return self.snapshot()

    def snapshot(self):
        return {
            'activeIndex': self.active_index,
            'foundIndex': self.found_index,
            'checkedIndices': list(self.checked_indices),
            'arrayValues': [_serialize(x) for x in super().__iter__()],
            'activeNodeId': None,
            'activeNodeIds': [],
            'foundNodeId': None,
            'visitedNodes': [],
            'activeEdge': None,
            'visitedEdges': [],
        }

    def finalize_steps(self, trace_steps, is_paused_for_choice=False):
        pass


def create_visual_ds(payload):
    return VisualArray(payload if isinstance(payload, list) else [])