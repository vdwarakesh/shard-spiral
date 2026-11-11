# python/graph.py

class _NodeId(str):
    """String subclass tagging graph node IDs so _serialize automatically
    converts them to display labels."""
    pass


class _GraphNeighborList(list):
    """In 'auto' mode, iterates in standard order.
    In 'manual' mode, prompts the user whenever 2 or more incident edges remain."""
    def __init__(self, graph, source_key, neighbors):
        super().__init__(neighbors)
        self._graph = graph
        self._source = str(source_key)

    def _iterate_items(self, items_list):
        if _sim_mode != 'manual':
            for nb in items_list:
                self._graph._on_edge_inspect(self._source, nb)
                yield nb
            self._graph._on_neighbor_loop_end(self._source)
            return

        remaining = list(items_list)
        while remaining:
            if len(remaining) > 1:
                if _user_choices:
                    chosen_id = str(_user_choices.pop(0))
                    match_idx = next(
                        (i for i, nb in enumerate(remaining)
                         if (str(nb[0]) if isinstance(nb, tuple) else str(nb)) == chosen_id),
                        0
                    )
                    nb = remaining.pop(match_idx)
                else:
                    src_label = _node_labels.get(self._source, self._source)
                    candidates = []
                    for nb in remaining:
                        nb_id = str(nb[0]) if isinstance(nb, tuple) else str(nb)
                        nb_label = _node_labels.get(nb_id, nb_id)
                        candidates.append({
                            'id': nb_id,
                            'label': nb_label,
                            'edge': [self._source, nb_id],
                            'edgeLabel': f"{src_label} → {nb_label}"
                        })
                    sys.settrace(None)
                    raise _WaitForUserChoice({
                        'type': 'select_neighbor',
                        'sourceNodeId': self._source,
                        'candidateNodeIds': [c['id'] for c in candidates],
                        'candidateEdges': [c['edge'] for c in candidates],
                        'candidates': candidates,
                        'title': f"Choose the next neighbor of '{src_label}' to inspect",
                        'reason': (
                            f"Node '{src_label}' has {len(candidates)} remaining incident edges to inspect "
                            f"({', '.join(c['label'] for c in candidates)}). "
                            f"Select any of these neighbors/edges to check whether it has been visited yet:"
                        )
                    })
            else:
                nb = remaining.pop(0)

            self._graph._on_edge_inspect(self._source, nb)
            yield nb

        self._graph._on_neighbor_loop_end(self._source)

    def __iter__(self):
        return self._iterate_items(super().__iter__())

    def __reversed__(self):
        return self._iterate_items(super().__reversed__())


class VisualGraph(dict):
    """Graph proxy exclusively for adjacency list {u: [v1, v2, ...]}."""
    def __init__(self, raw_adj):
        wrapped = {}
        for k, neighbors in (raw_adj or {}).items():
            uk = _NodeId(str(k))
            nb_list = []
            for nb in neighbors:
                if isinstance(nb, (list, tuple)) and len(nb) >= 2:
                    nb_list.append((_NodeId(str(nb[0])), nb[1]))
                else:
                    nb_list.append(_NodeId(str(nb)))
            wrapped[uk] = nb_list
        super().__init__(wrapped)

        self._incident_edges = {str(k): [] for k in wrapped.keys()}
        for u_key, nb_list in wrapped.items():
            u_str = str(u_key)
            for nb in nb_list:
                v_str = str(nb[0]) if isinstance(nb, tuple) else str(nb)
                edge = (u_str, v_str)
                if edge not in self._incident_edges.setdefault(u_str, []):
                    self._incident_edges[u_str].append(edge)
                if edge not in self._incident_edges.setdefault(v_str, []):
                    self._incident_edges[v_str].append(edge)

        self.active_node = None
        self._discovered_nodes = set()
        self.active_edge = None
        self.visited_edges = []
        self.step_accessed_nodes = set()
        self._loop_exhausted_on_step = False

    def on_step_start(self):
        self.step_accessed_nodes.clear()
        self._loop_exhausted_on_step = False

    def record_visit(self, node_key):
        s_key = str(node_key)
        if s_key not in self:
            return
        self.active_node = s_key
        self.step_accessed_nodes.add(s_key)
        self._discovered_nodes.add(s_key)

    def _on_edge_inspect(self, u_key, v_entry):
        u_str = str(u_key)
        v_str = str(v_entry[0]) if isinstance(v_entry, tuple) else str(v_entry)
        self._loop_exhausted_on_step = False
        self.record_visit(u_str)
        self.active_edge = [u_str, v_str]
        if v_str in self:
            self.step_accessed_nodes.add(v_str)

    def _on_neighbor_loop_end(self, u_key):
        self.active_edge = None
        self._loop_exhausted_on_step = True
        self.record_visit(str(u_key))

    def _promote_discovered_edges(self, frame_locals):
        for name, val in frame_locals.items():
            if isinstance(val, (list, tuple, set, deque)):
                for item in val:
                    if isinstance(item, _NodeId) or str(item) in self:
                        self._discovered_nodes.add(str(item))
                    elif isinstance(item, (list, tuple)) and len(item) >= 2:
                        for sub in item:
                            if isinstance(sub, _NodeId) or (isinstance(sub, str) and sub in self):
                                self._discovered_nodes.add(str(sub))
            elif isinstance(val, dict) and val is not self:
                for k, v in val.items():
                    if (isinstance(k, _NodeId) or str(k) in self) and v is not None and v != float('inf'):
                        self._discovered_nodes.add(str(k))
                    if isinstance(v, _NodeId) and str(v) in self:
                        self._discovered_nodes.add(str(v))

        if not self.active_edge:
            return
        u_str, v_str = self.active_edge
        if v_str in self._discovered_nodes:
            pair = [u_str, v_str]
            if pair not in self.visited_edges:
                self.visited_edges.append(pair)

    def __getitem__(self, key):
        s_key = _NodeId(str(key))
        if s_key in self:
            self.record_visit(s_key)
            return _GraphNeighborList(self, s_key, super().__getitem__(s_key))
        return super().__getitem__(key)

    def get(self, key, default=None):
        s_key = _NodeId(str(key))
        if s_key in self:
            return self[s_key]
        return default

    def __iter__(self):
        for k in super().__iter__():
            yield _NodeId(k)

    def keys(self):
        return [_NodeId(k) for k in super().keys()]

    def on_line_fallback(self, loop_target_vars, frame_locals, is_while_line=False):
        if is_while_line:
            self.active_edge = None
            self.active_node = None
        elif not self.active_edge and not self._loop_exhausted_on_step:
            for val in loop_target_vars:
                if isinstance(val, _NodeId) and str(val) in self:
                    self.record_visit(str(val))
                    break
        self._promote_discovered_edges(frame_locals)

    def enhance_state_vars(self, state_vars, frame_locals, first_param_name):
        pass

    def on_return(self, ret_val):
        self.active_node = None
        self.active_edge = None
        self.step_accessed_nodes.clear()
        return self.snapshot()

    def snapshot(self):
        active_nodes = []
        if self.active_node is not None:
            active_nodes.append(self.active_node)
        if self.active_edge:
            for endpoint in self.active_edge:
                if endpoint not in active_nodes:
                    active_nodes.append(endpoint)
        return {
            'activeIndex': -1,
            'foundIndex': -1,
            'checkedIndices': [],
            'activeNodeId': self.active_node,
            'activeNodeIds': active_nodes,
            'foundNodeId': None,
            'visitedNodes': [],
            'activeEdge': self.active_edge,
            'visitedEdges': list(self.visited_edges),
            '_accessed': list(self.step_accessed_nodes),
        }

    def finalize_steps(self, trace_steps, is_paused_for_choice=False):
        last_access_step = {}
        first_access_step = {}

        for step_idx, step in enumerate(trace_steps):
            vis = step['visual']
            accessed = vis.pop('_accessed', [])
            if vis['activeNodeId'] is not None and vis['activeNodeId'] not in accessed:
                accessed.append(vis['activeNodeId'])
            if vis.get('activeEdge'):
                for ep in vis['activeEdge']:
                    if str(ep) not in accessed:
                        accessed.append(str(ep))
            for node_id in accessed:
                s_id = str(node_id)
                if s_id not in first_access_step:
                    first_access_step[s_id] = step_idx
                last_access_step[s_id] = step_idx

        ever_accessed_in_order = sorted(first_access_step.keys(), key=lambda k: first_access_step[k])

        for step_idx, step in enumerate(trace_steps):
            vis = step['visual']
            active = vis['activeNodeId']
            active_set = set(str(x) for x in (vis.get('activeNodeIds') or []))
            if active is not None:
                active_set.add(str(active))
            if vis.get('activeEdge'):
                for ep in vis['activeEdge']:
                    active_set.add(str(ep))
            found = vis['foundNodeId']

            visited_edge_set = set(
                (str(e[0]), str(e[1])) for e in (vis.get('visitedEdges') or [])
                if isinstance(e, (list, tuple)) and len(e) >= 2
            )

            visited = []
            for k in ever_accessed_in_order:
                if first_access_step[k] >= step_idx:
                    continue
                if k in active_set or k == found:
                    continue
                inc_edges = self._incident_edges.get(k, [])
                all_inc_visited = bool(inc_edges) and all(e in visited_edge_set for e in inc_edges)

                if is_paused_for_choice:
                    if all_inc_visited:
                        visited.append(k)
                else:
                    if all_inc_visited or last_access_step[k] < step_idx:
                        visited.append(k)

            vis['visitedNodes'] = visited


def create_visual_ds(payload):
    return VisualGraph(payload if isinstance(payload, dict) else {})