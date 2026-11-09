import sys
import json
import inspect
import traceback
import ast
import math
from collections import deque

_trace_steps = []
_error_info = None
_step_count = 0
_pending_steps = {}

class _StepLimitExceeded(Exception):
    pass

_payload = json.loads(_ds_payload_json)
_node_labels = json.loads(_node_labels_json)
_user_choices = list(json.loads(_user_choices_json))

# Map display labels to canonical node keys first, then fallback to internal IDs
_label_to_key = {}
for _k in _node_labels.keys():
    _label_to_key[str(_k)] = str(_k)
for _k, _lbl in _node_labels.items():
    _label_to_key[str(_lbl)] = str(_k)


class _NodeId(str):
    """String subclass tagging graph node IDs so _serialize automatically
    converts them to display labels."""
    pass


class _WaitForUserChoice(Exception):
    def __init__(self, interaction):
        self.interaction = interaction


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
                    # Stop tracing BEFORE raising so Python does not emit a fake 'return' event
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
        for k, neighbors in raw_adj.items():
            uk = _NodeId(str(k))
            nb_list = []
            for nb in neighbors:
                if isinstance(nb, (list, tuple)) and len(nb) >= 2:
                    nb_list.append((_NodeId(str(nb[0])), nb[1]))
                else:
                    nb_list.append(_NodeId(str(nb)))
            wrapped[uk] = nb_list
        super().__init__(wrapped)

        # Precompute all incident edges (outgoing and incoming) per node
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
                        # Support priority queue tuples like (dist, node) or (weight, u, v)
                        for sub in item:
                            if isinstance(sub, _NodeId) or (isinstance(sub, str) and sub in self):
                                self._discovered_nodes.add(str(sub))
            elif isinstance(val, dict) and val is not self:
                # Support dict trackers like parent = {v: u} or dist = {v: d}
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
            # When evaluating a `while` loop header (e.g. `while queue:`),
            # clear active_edge and active_node so the previously inspected
            # neighbor/node doesn't stay highlighted during the queue check.
            self.active_edge = None
            self.active_node = None
        elif not self.active_edge and not self._loop_exhausted_on_step:
            for val in loop_target_vars:
                if isinstance(val, _NodeId) and str(val) in self:
                    self.record_visit(str(val))
                    break
        self._promote_discovered_edges(frame_locals)

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

            # Set of edges already visited by this step
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
                # A node is completely visited if:
                # 1. All of its incident edges (outgoing and incoming) have been visited, OR
                # 2. The full run finished (not paused) and it is never accessed again at or after step_idx
                inc_edges = self._incident_edges.get(k, [])
                all_inc_visited = bool(inc_edges) and all(e in visited_edge_set for e in inc_edges)

                if is_paused_for_choice:
                    if all_inc_visited:
                        visited.append(k)
                else:
                    if all_inc_visited or last_access_step[k] < step_idx:
                        visited.append(k)

            vis['visitedNodes'] = visited


def _serialize(v):
    if isinstance(v, _NodeId):
        return _node_labels.get(str(v), str(v))
    if isinstance(v, bool) or v is None:
        return v
    if isinstance(v, float):
        if math.isinf(v):
            return "∞" if v > 0 else "-∞"
        if math.isnan(v):
            return "NaN"
        return round(v, 4) if v != int(v) else int(v)
    if isinstance(v, (int, str)):
        return v
    if isinstance(v, (list, tuple, set, deque)):
        return [_serialize(x) for x in v]
    if isinstance(v, dict):
        return {str(_serialize(k)): _serialize(val) for k, val in v.items()}
    return repr(v)


def _build_ast_line_info(code_str):
    loop_targets = {}
    assign_targets = {}
    while_lines = set()
    top_level_funcs = []
    try:
        tree = ast.parse(code_str)
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and not node.name.startswith('__'):
                top_level_funcs.append(node.name)
        for node in ast.walk(tree):
            if isinstance(node, (ast.For, ast.AsyncFor)) and hasattr(node, 'lineno'):
                names = [
                    sub.id for sub in ast.walk(node.target)
                    if isinstance(sub, ast.Name) and isinstance(sub.ctx, ast.Store)
                ]
                if names:
                    loop_targets.setdefault(node.lineno, []).extend(names)
            elif isinstance(node, ast.Assign) and hasattr(node, 'lineno'):
                names = [
                    sub.id for t in node.targets for sub in ast.walk(t)
                    if isinstance(sub, ast.Name) and isinstance(sub.ctx, ast.Store)
                ]
                if names:
                    assign_targets.setdefault(node.lineno, []).extend(names)
            elif isinstance(node, ast.AnnAssign) and hasattr(node, 'lineno') and node.target:
                names = [
                    sub.id for sub in ast.walk(node.target)
                    if isinstance(sub, ast.Name) and isinstance(sub.ctx, ast.Store)
                ]
                if names:
                    assign_targets.setdefault(node.lineno, []).extend(names)
            elif isinstance(node, ast.While) and hasattr(node, 'lineno'):
                while_lines.add(node.lineno)
    except Exception:
        pass
    return loop_targets, assign_targets, while_lines, top_level_funcs


def _extract_algo_line(exc_tb):
    tb_list = traceback.extract_tb(exc_tb)
    for frame_summary in reversed(tb_list):
        if frame_summary.filename == '<algorithm>':
            return frame_summary.lineno
    return _trace_steps[-1]['line'] if _trace_steps else None


try:
    _ns = {}
    exec(compile(_user_code, '<algorithm>', 'exec'), _ns)

    _loop_targets, _assign_targets, _while_lines, _top_level_funcs = _build_ast_line_info(_user_code)

    # Guard against __init__ or missing function names by picking the first top-level function
    if (_func_name not in _ns or _func_name.startswith('__')) and _top_level_funcs:
        _func_name = _top_level_funcs[0]

    if _func_name not in _ns:
        raise NameError(f"Function '{_func_name}' was not found in the algorithm file.")

    _fn = _ns[_func_name]
    _sig_params = list(inspect.signature(_fn).parameters.keys())
    _param_names = set(_sig_params)
    _first_param = _sig_params[0] if _sig_params else 'graph'
    _exhausted_loop_vars = set()

    _visual_ds = VisualGraph(_payload)

    _raw_kwargs = json.loads(_raw_kwargs_json)
    _eval_kwargs = {}
    for _k, _v_str in _raw_kwargs.items():
        try:
            _val = ast.literal_eval(_v_str)
        except (ValueError, SyntaxError):
            _val = _v_str
        if _val is not None:
            _s = str(_val).strip()
            if _s in _label_to_key:
                _val = _NodeId(_label_to_key[_s])
        _eval_kwargs[_k] = _val

    def _build_state_vars(frame, executed_lineno):
        loc = {}
        curr_f = frame
        frames_chain = []
        while curr_f is not None and curr_f.f_code.co_filename == '<algorithm>':
            frames_chain.append(curr_f)
            curr_f = curr_f.f_back
        for f_item in reversed(frames_chain):
            loc.update(f_item.f_locals)

        loop_var_names = _loop_targets.get(executed_lineno, [])
        if loop_var_names:
            if _visual_ds._loop_exhausted_on_step:
                # The `for` loop just terminated; mark its target variable(s) as exhausted
                _exhausted_loop_vars.update(loop_var_names)
            else:
                # The `for` loop is actively yielding a new item
                _exhausted_loop_vars.difference_update(loop_var_names)

        loop_var_vals = [
            loc[name] for name in loop_var_names
            if name in loc and name not in _param_names and name not in _exhausted_loop_vars
        ]
        _visual_ds.on_line_fallback(
            loop_var_vals,
            loc,
            is_while_line=(executed_lineno in _while_lines)
        )

        # Only highlight newly assigned node variables on this specific line
        # (e.g. `node = queue.pop(0)`, `_, u = heapq.heappop(pq)`, `v = parent[v]`)
        assigned_names = _assign_targets.get(executed_lineno, [])
        if assigned_names and not _visual_ds._loop_exhausted_on_step:
            _visual_ds.active_edge = None
            for name in assigned_names:
                val = loc.get(name)
                if isinstance(val, _NodeId) and str(val) in _visual_ds:
                    _visual_ds.record_visit(str(val))
                elif isinstance(val, (list, tuple)):
                    for item in val:
                        if isinstance(item, _NodeId) and str(item) in _visual_ds:
                            _visual_ds.record_visit(str(item))

        state_vars = {}
        for k, v in loc.items():
            if (
                not k.startswith('_')
                and k != _first_param
                and k not in _exhausted_loop_vars
                and not inspect.isfunction(v)
                and not inspect.ismodule(v)
            ):
                state_vars[k] = _serialize(v)
        return state_vars

    def _tracer(frame, event, arg):
        global _step_count
        if frame.f_code.co_filename != '<algorithm>':
            return _tracer
        if event not in ('call', 'line', 'return'):
            return _tracer

        _step_count += 1
        if _step_count > _MAX_STEPS:
            raise _StepLimitExceeded(
                f"Execution exceeded {_MAX_STEPS} steps (possible infinite loop)."
            )

        if event == 'call':
            caller = frame.f_back
            if caller is not None and caller.f_code.co_filename == '<algorithm>':
                caller_fid = id(caller)
                caller_pending = _pending_steps.pop(caller_fid, None)
                if caller_pending is not None:
                    caller_state = _build_state_vars(caller, caller_pending['line'])
                    _trace_steps.append({
                        'event': 'line',
                        'line': caller_pending['line'],
                        'stateVars': caller_state,
                        'visual': _visual_ds.snapshot(),
                    })
            return _tracer

        fid = id(frame)
        pending = _pending_steps.pop(fid, None)
        executed_line = pending['line'] if pending is not None else frame.f_lineno

        state_vars = _build_state_vars(frame, executed_line)

        if pending is not None and not (event == 'return' and pending['line'] == frame.f_lineno):
            _trace_steps.append({
                'event': 'line',
                'line': pending['line'],
                'stateVars': state_vars,
                'visual': _visual_ds.snapshot(),
            })

        if event == 'line':
            _visual_ds.on_step_start()
            _pending_steps[fid] = {'line': frame.f_lineno}
        else:  # 'return'
            if frame.f_code.co_name == _func_name:
                ret_val = _serialize(arg)
                ret_state_vars = dict(state_vars)
                ret_state_vars['return'] = ret_val
                final_visual = _visual_ds.on_return(arg)

                _trace_steps.append({
                    'event': 'return',
                    'line': frame.f_lineno,
                    'stateVars': ret_state_vars,
                    'visual': final_visual,
                })

        return _tracer

    _old_rec_limit = sys.getrecursionlimit()
    sys.setrecursionlimit(250)

    sys.settrace(_tracer)
    try:
        _fn(_visual_ds, **_eval_kwargs)
    finally:
        sys.settrace(None)
        sys.setrecursionlimit(_old_rec_limit)

    _visual_ds.finalize_steps(_trace_steps)

except _WaitForUserChoice as pause_exc:
    # Flush the line where the choice was triggered (e.g. 'for neighbor in graph[node]:')
    # and clear activeNodeId / activeNodeIds / activeEdge on this step so ONLY
    # interaction.candidateNodeIds and interaction.candidateEdges are highlighted!
    _, _, _tb = sys.exc_info()
    _pause_frame = None
    _curr_tb = _tb
    while _curr_tb is not None:
        if _curr_tb.tb_frame.f_code.co_filename == '<algorithm>':
            _pause_frame = _curr_tb.tb_frame
        _curr_tb = _curr_tb.tb_next

    if _pause_frame is not None:
        _pfid = id(_pause_frame)
        _pending = _pending_steps.pop(_pfid, None)
        _pline = _pending['line'] if _pending is not None else _pause_frame.f_lineno
        _pstate = _build_state_vars(_pause_frame, _pline)
        for _lvar in _loop_targets.get(_pline, []):
            _pstate.pop(_lvar, None)
        _pvis = _visual_ds.snapshot()
        _src_id = pause_exc.interaction.get('sourceNodeId')
        _pvis['activeNodeId'] = _src_id
        _pvis['activeNodeIds'] = [_src_id] if _src_id is not None else []
        _pvis['activeEdge'] = None
        _trace_steps.append({
            'event': 'line',
            'line': _pline,
            'stateVars': _pstate,
            'visual': _pvis,
        })

    _visual_ds.finalize_steps(_trace_steps, is_paused_for_choice=True)
    if _trace_steps:
        _trace_steps[-1]['interaction'] = pause_exc.interaction

except _StepLimitExceeded as e:
    _visual_ds.finalize_steps(_trace_steps)
    _error_info = {
        'type': 'InfiniteLoopError',
        'message': str(e),
        'line': _trace_steps[-1]['line'] if _trace_steps else 1
    }
except RecursionError:
    _visual_ds.finalize_steps(_trace_steps)
    _, _, _tb = sys.exc_info()
    _error_info = {
        'type': 'RecursionError',
        'message': 'Maximum recursion depth exceeded.',
        'line': _extract_algo_line(_tb)
    }
except SyntaxError as e:
    _error_info = {
        'type': 'SyntaxError',
        'message': f"{e.msg} (line {e.lineno})",
        'line': e.lineno
    }
except Exception as e:
    if '_visual_ds' in locals():
        _visual_ds.finalize_steps(_trace_steps)
    _, _, _tb = sys.exc_info()
    _error_info = {
        'type': type(e).__name__,
        'message': str(e),
        'line': _extract_algo_line(_tb)
    }

json.dumps({
    'steps': _trace_steps,
    'error': _error_info
})