import sys
import json
import inspect
import traceback
import ast
import math
import heapq
from collections import deque, OrderedDict

_trace_steps = []
_error_info = None
_step_count = 0
_pending_steps = {}

class _StepLimitExceeded(Exception):
    pass

_payload = json.loads(_ds_payload_json)
_node_labels = json.loads(_node_labels_json)
_user_choices = list(json.loads(_user_choices_json))

# Normalize dsCategory string (e.g. "Doubly Linked List" -> "doubly_linked_list")
def _norm_cat(cat_str):
    if not cat_str:
        return 'array'
    return str(cat_str).strip().lower().replace('-', '_').replace(' ', '_')

_NORM_CATEGORY = _norm_cat(_ds_category)

# Map display labels to canonical node keys first, then fallback to internal IDs
_label_to_key = {}
for _k in _node_labels.keys():
    _label_to_key[str(_k)] = str(_k)
for _k, _lbl in _node_labels.items():
    _label_to_key[str(_lbl)] = str(_k)


# ============================================================================
# 0. DYNAMIC USER-CHOICE BRANCHING PLUGIN
# ============================================================================

class _WaitForUserChoice(Exception):
    def __init__(self, interaction):
        self.interaction = interaction


class _ChoicePlugin:
    """Extensible branching plugin. Supports both automatic proxy hooks (graphs,
    trees, matrices) and explicit user/algorithm calls via choose(...)."""
    @staticmethod
    def branch(candidates, choice_type='generic_choice', title='Select next branch', reason='Choose the next option to explore:', extra=None):
        items = list(candidates)
        if not items:
            return None
        if len(items) == 1 or _sim_mode != 'manual':
            return items[0]

        if _user_choices:
            chosen_raw = str(_user_choices.pop(0))
            for item in items:
                item_id = str(item.get('id', item)) if isinstance(item, dict) else str(item[0] if isinstance(item, tuple) else item)
                if item_id == chosen_raw:
                    return item
            return items[0]

        formatted_candidates = []
        for item in items:
            if isinstance(item, dict) and 'id' in item:
                formatted_candidates.append(item)
            else:
                raw_id = str(item[0]) if isinstance(item, tuple) else str(item)
                lbl = _node_labels.get(raw_id, raw_id)
                formatted_candidates.append({'id': raw_id, 'label': lbl, 'value': _serialize(item)})

        payload = {
            'type': choice_type,
            'candidateNodeIds': [c['id'] for c in formatted_candidates],
            'candidates': formatted_candidates,
            'title': title,
            'reason': reason,
        }
        if extra:
            payload.update(extra)
        raise _WaitForUserChoice(payload)


def choose(options, title="Choose next step", reason="Multiple valid branches exist. Select one to continue:"):
    """Global helper injected into algorithm namespace so any algorithm can
    dynamically request user branching in 'manual' mode."""
    opts = list(options)
    selected = _ChoicePlugin.branch(opts, choice_type='custom_choice', title=title, reason=reason)
    return selected


# ============================================================================
# 1. GENERIC PROXY DATA STRUCTURES (WITH EXACT FUTURE-ACCESS TRACKING)
# ============================================================================

class _NodeId(str):
    """String subclass tagging graph/tree/linked-list node IDs so _serialize
    automatically converts them to display labels."""
    pass


def _base_visual_dict(**overrides):
    """Standardized snapshot schema ensuring backward compatibility with existing
    Array & Graph renderers while providing rich state for all 29 structures."""
    base = {
        'dsType': _NORM_CATEGORY,
        'activeIndex': -1,
        'foundIndex': -1,
        'checkedIndices': [],
        'activeNodeId': None,
        'activeNodeIds': [],
        'foundNodeId': None,
        'visitedNodes': [],
        'activeEdge': None,
        'visitedEdges': [],
    }
    base.update(overrides)
    return base


def _finalize_node_steps(trace_steps, is_paused_for_choice=False):
    """Computes visitedNodes for node-based structures (Graphs, Trees, Linked Lists, Hash).
    A node is only marked as 'visited' (completely finished) at step_idx if:
      1. It was first directly accessed before step_idx (first_access_step[k] < step_idx)
      2. It will NEVER be accessed or held in an active call-stack frame at or after step_idx
         (last_active_or_access_step[k] < step_idx)
      3. When paused for a manual user choice, any node currently held in the call stack
         or frontier (`_in_flight`) is still pending future work and is NOT marked visited.
    """
    last_access_step = {}
    first_access_step = {}

    for step_idx, step in enumerate(trace_steps):
        vis = step['visual']
        accessed = vis.pop('_accessed', [])
        in_flight = vis.pop('_in_flight', [])

        if vis.get('activeNodeId') is not None and str(vis['activeNodeId']) not in accessed:
            accessed.append(str(vis['activeNodeId']))

        for node_id in accessed:
            s_id = str(node_id)
            if s_id not in first_access_step:
                first_access_step[s_id] = step_idx
            last_access_step[s_id] = step_idx

        # Any node still held in a caller's frame (e.g. parent during DFS recursion)
        # will be returned to later, so extend its last_access_step at least to step_idx.
        for node_id in in_flight:
            s_id = str(node_id)
            if s_id in first_access_step:
                last_access_step[s_id] = max(last_access_step.get(s_id, step_idx), step_idx)

    # If paused for user choice on the last step, any node still in_flight at the final step
    # has not finished execution yet.
    final_in_flight = set()
    if is_paused_for_choice and trace_steps:
        last_vis = trace_steps[-1]['visual']
        final_in_flight.update(str(x) for x in (last_vis.get('activeNodeIds') or []))
        if last_vis.get('activeNodeId') is not None:
            final_in_flight.add(str(last_vis['activeNodeId']))

    ever_accessed_in_order = sorted(first_access_step.keys(), key=lambda k: first_access_step[k])
    for step_idx, step in enumerate(trace_steps):
        vis = step['visual']
        active = vis.get('activeNodeId')
        active_set = set(str(x) for x in (vis.get('activeNodeIds') or []))
        if active is not None:
            active_set.add(str(active))
        found = str(vis['foundNodeId']) if vis.get('foundNodeId') is not None else None

        visited = [
            k for k in ever_accessed_in_order
            if first_access_step[k] < step_idx
            and last_access_step[k] < step_idx
            and (not is_paused_for_choice or k not in final_in_flight)
            and k not in active_set
            and k != found
        ]
        vis['visitedNodes'] = visited


# ----------------------------------------------------------------------------
# 1A. LINEAR SEQUENCES, QUEUES, STACKS, STRINGS, HEAPS
# ----------------------------------------------------------------------------

class VisualSequence(list):
    def __init__(self, iterable, param_name='arr', subtype='array', capacity=None):
        if isinstance(iterable, str):
            init_items = list(iterable)
            subtype = 'string'
        elif isinstance(iterable, dict) and 'items' in iterable:
            init_items = list(iterable.get('items', []))
            capacity = iterable.get('capacity', capacity)
        elif isinstance(iterable, (list, tuple, deque, set)):
            init_items = list(iterable)
        else:
            init_items = [iterable] if iterable is not None else []

        super().__init__(init_items)
        self.param_name = param_name
        self.subtype = subtype
        self.capacity = capacity
        self.active_index = -1
        self.recent_accesses = {}
        self.step_accessed_indices = set()
        self.in_flight_indices = set()
        self.last_op = None

    def on_step_start(self):
        self.active_index = -1
        self.recent_accesses.clear()
        self.step_accessed_indices.clear()
        self.in_flight_indices.clear()
        self.last_op = None

    def _record_access(self, idx):
        if isinstance(idx, int) and not isinstance(idx, bool):
            norm_idx = idx if idx >= 0 else len(self) + idx
            if 0 <= norm_idx < len(self):
                self.active_index = norm_idx
                self.step_accessed_indices.add(norm_idx)
                val = super().__getitem__(norm_idx)
                self.recent_accesses[f"{self.param_name}[{norm_idx}]"] = val

    def __getitem__(self, idx):
        if isinstance(idx, slice):
            start, stop, step = idx.indices(len(self))
            for i in range(start, stop, step):
                self._record_access(i)
            res = super().__getitem__(idx)
            return ''.join(str(x) for x in res) if self.subtype == 'string' else res
        self._record_access(idx)
        return super().__getitem__(idx)

    def __setitem__(self, idx, val):
        if not isinstance(idx, slice):
            super().__setitem__(idx, val)
            self._record_access(idx)
            self.last_op = 'set'
            return
        super().__setitem__(idx, val)

    def insert(self, idx, val):
        super().insert(idx, val)
        self.last_op = 'insert'
        norm_idx = max(0, min(idx if idx >= 0 else len(self) + idx, len(self) - 1))
        self._record_access(norm_idx)

    def append(self, val):
        if self.capacity and len(self) >= self.capacity and self.subtype == 'circular_queue':
            super().pop(0)
        super().append(val)
        self.last_op = 'append'
        self._record_access(len(self) - 1)

    def push(self, val, priority=None):
        item = (priority, val) if priority is not None else val
        if self.subtype in ('heap', 'binary_heap', 'min_heap', 'priority_queue'):
            heapq.heappush(self, item)
            self.last_op = 'heappush'
            self._record_access(0)
        elif self.subtype == 'max_heap':
            super().append(item)
            self.sort(reverse=True)
            self.last_op = 'heappush_max'
            self._record_access(0)
        else:
            self.append(item)

    def enqueue(self, val):
        self.append(val)
        self.last_op = 'enqueue'

    def appendleft(self, val):
        super().insert(0, val)
        self.last_op = 'appendleft'
        self._record_access(0)

    def pop(self, idx=-1):
        if not self:
            raise IndexError("pop from empty structure")
        norm_idx = idx if idx >= 0 else len(self) + idx
        self._record_access(norm_idx)
        val = super().pop(idx)
        self.last_op = 'pop'
        self.active_index = min(norm_idx, len(self) - 1) if self else -1
        return val

    def popleft(self):
        if not self:
            raise IndexError("popleft from empty deque/queue")
        self._record_access(0)
        val = super().pop(0)
        self.last_op = 'popleft'
        self.active_index = 0 if self else -1
        return val

    def dequeue(self):
        return self.popleft()

    def heappop(self):
        if not self:
            raise IndexError("heappop from empty heap")
        if self.subtype == 'max_heap':
            self.sort(reverse=True)
            self._record_access(0)
            return super().pop(0)
        val = heapq.heappop(self)
        self._record_access(0)
        return val

    def heappush(self, val):
        self.push(val)

    def peek(self):
        if not self:
            return None
        idx = 0 if self.subtype in ('queue', 'circular_queue', 'priority_queue', 'heap', 'binary_heap', 'min_heap', 'max_heap') else len(self) - 1
        self._record_access(idx)
        return super().__getitem__(idx)

    def lower(self):
        return ''.join(str(x).lower() for x in self)

    def upper(self):
        return ''.join(str(x).upper() for x in self)

    def split(self, sep=None):
        return ''.join(str(x) for x in self).split(sep)

    def __str__(self):
        if self.subtype == 'string':
            return ''.join(str(x) for x in self)
        return super().__str__()

    def __eq__(self, other):
        if isinstance(other, str) and self.subtype == 'string':
            return ''.join(str(x) for x in self) == other
        return super().__eq__(other)

    def on_line_fallback(self, loop_target_vars, frame_locals, all_frames_locals=None):
        if not self.recent_accesses:
            for var_val in loop_target_vars:
                if isinstance(var_val, int) and not isinstance(var_val, bool) and 0 <= var_val < len(self):
                    self._record_access(var_val)
                    break

    def enhance_state_vars(self, state_vars):
        for expr_str, val in self.recent_accesses.items():
            state_vars[expr_str] = _serialize(val)

    def on_return(self, ret_val):
        found_idx = -1
        if isinstance(ret_val, int) and not isinstance(ret_val, bool) and 0 <= ret_val < len(self):
            found_idx = ret_val
        self.active_index = -1
        self.step_accessed_indices.clear()
        self.in_flight_indices.clear()
        return self.snapshot(found_idx)

    def snapshot(self, found_index=-1):
        act_idx = found_index if found_index >= 0 else self.active_index
        snap = _base_visual_dict(
            dsType=self.subtype,
            activeIndex=act_idx,
            foundIndex=found_index,
            checkedIndices=[],
            elements=[_serialize(x) for x in self],
            lastOp=self.last_op,
            _accessed=list(self.step_accessed_indices),
            _in_flight=list(self.in_flight_indices),
        )
        if self.subtype in ('heap', 'binary_heap', 'min_heap', 'max_heap', 'priority_queue'):
            heap_nodes = [{'id': str(i), 'label': str(_serialize(v)), 'index': i} for i, v in enumerate(self)]
            heap_edges = []
            for i in range(len(self)):
                l, r = 2 * i + 1, 2 * i + 2
                if l < len(self):
                    heap_edges.append({'from': str(i), 'to': str(l)})
                if r < len(self):
                    heap_edges.append({'from': str(i), 'to': str(r)})
            snap['activeNodeId'] = str(act_idx) if act_idx >= 0 else None
            snap['activeNodeIds'] = [str(act_idx)] if act_idx >= 0 else []
            snap['nodes'] = heap_nodes
            snap['edges'] = heap_edges
        return snap

    def finalize_steps(self, trace_steps, is_paused_for_choice=False):
        last_access_step = {}
        first_access_step = {}

        for step_idx, step in enumerate(trace_steps):
            vis = step['visual']
            accessed = vis.pop('_accessed', [])
            in_flight = vis.pop('_in_flight', [])
            if vis['activeIndex'] >= 0 and vis['activeIndex'] not in accessed:
                accessed.append(vis['activeIndex'])
            for arr_idx in accessed:
                if arr_idx not in first_access_step:
                    first_access_step[arr_idx] = step_idx
                last_access_step[arr_idx] = step_idx
            for arr_idx in in_flight:
                if arr_idx in first_access_step:
                    last_access_step[arr_idx] = max(last_access_step.get(arr_idx, step_idx), step_idx)

        ever_accessed_in_order = sorted(first_access_step.keys(), key=lambda k: first_access_step[k])

        for step_idx, step in enumerate(trace_steps):
            vis = step['visual']
            active = vis['activeIndex']
            found = vis['foundIndex']
            checked = [
                k for k in ever_accessed_in_order
                if first_access_step[k] < step_idx
                and last_access_step[k] < step_idx
                and k != active
                and k != found
            ]
            vis['checkedIndices'] = checked
            if self.subtype in ('heap', 'binary_heap', 'min_heap', 'max_heap', 'priority_queue'):
                vis['visitedNodes'] = [str(k) for k in checked]


# ----------------------------------------------------------------------------
# 1B. LINKED LISTS
# ----------------------------------------------------------------------------

class ListNode:
    def __init__(self, val, node_id, owner):
        object.__setattr__(self, '_val', val)
        object.__setattr__(self, '_id', _NodeId(str(node_id)))
        object.__setattr__(self, '_next', None)
        object.__setattr__(self, '_prev', None)
        object.__setattr__(self, '_owner', owner)
        owner._register_node(self)

    @property
    def id(self): return self._id

    @property
    def val(self):
        self._owner._record_node_access(self)
        return self._val

    @val.setter
    def val(self, value):
        object.__setattr__(self, '_val', value)
        self._owner._record_node_access(self)

    @property
    def data(self): return self.val
    @data.setter
    def data(self, value): self.val = value
    @property
    def value(self): return self.val
    @value.setter
    def value(self, value): self.val = value

    @property
    def next(self):
        self._owner._record_node_access(self)
        nxt = self._next
        if nxt is not None:
            self._owner._record_edge_access(self._id, nxt._id)
        return nxt

    @next.setter
    def next(self, target):
        object.__setattr__(self, '_next', target)
        self._owner._record_node_access(self)
        if target is not None:
            self._owner._record_edge_access(self._id, target._id)

    @property
    def prev(self):
        self._owner._record_node_access(self)
        prv = self._prev
        if prv is not None:
            self._owner._record_edge_access(self._id, prv._id)
        return prv

    @prev.setter
    def prev(self, target):
        object.__setattr__(self, '_prev', target)
        self._owner._record_node_access(self)
        if target is not None:
            self._owner._record_edge_access(self._id, target._id)

    @property
    def head(self):
        self._owner._record_node_access(self)
        return self._owner.head

    @head.setter
    def head(self, node):
        self._owner.head = node

    def __iter__(self):
        curr = self
        visited_ids = set()
        while curr is not None and curr._id not in visited_ids:
            visited_ids.add(curr._id)
            self._owner._record_node_access(curr)
            yield curr
            curr = curr._next

    def __len__(self):
        return len(self._owner._reachable_nodes())

    def __getitem__(self, idx):
        nodes = self._owner._reachable_nodes()
        node = nodes[idx]
        self._owner._record_node_access(node)
        return node

    def __repr__(self):
        return f"ListNode({self._val!r})"


class VisualLinkedList:
    def __init__(self, payload, param_name='head', subtype='singly_linked_list'):
        self.param_name = param_name
        self.subtype = subtype
        self.is_doubly = 'doubly' in subtype
        self.is_circular = 'circular' in subtype
        self.all_nodes = OrderedDict()
        self.head = None
        self.tail = None
        self.active_node = None
        self.active_edge = None
        self.visited_edges = []
        self.step_accessed_nodes = set()
        self.in_flight_nodes = set()
        self.pointer_vars = {}
        self._build_from_payload(payload)

    def _register_node(self, node):
        self.all_nodes[str(node._id)] = node

    def _build_from_payload(self, payload):
        items = payload.get('values', payload.get('nodes', [])) if isinstance(payload, dict) else (payload or [])
        created = []
        for i, raw in enumerate(items):
            if isinstance(raw, dict):
                nid = str(raw.get('id', i))
                val = raw.get('val', raw.get('value', raw.get('label', i)))
            else:
                nid = str(i)
                val = raw
            node = ListNode(val, nid, self)
            created.append(node)

        for i in range(len(created)):
            if i + 1 < len(created):
                object.__setattr__(created[i], '_next', created[i + 1])
                if self.is_doubly:
                    object.__setattr__(created[i + 1], '_prev', created[i])

        if created:
            self.head = created[0]
            self.tail = created[-1]
            if self.is_circular:
                object.__setattr__(self.tail, '_next', self.head)
                if self.is_doubly:
                    object.__setattr__(self.head, '_prev', self.tail)

    def _reachable_nodes(self):
        res = []
        seen = set()
        curr = self.head
        while curr is not None and str(curr._id) not in seen:
            seen.add(str(curr._id))
            res.append(curr)
            curr = curr._next
        for nid, node in self.all_nodes.items():
            if nid not in seen:
                res.append(node)
        return res

    def _record_node_access(self, node):
        if node is None:
            return
        nid = str(node._id)
        self.active_node = nid
        self.step_accessed_nodes.add(nid)

    def _record_edge_access(self, u_id, v_id):
        u_s, v_s = str(u_id), str(v_id)
        self.active_edge = [u_s, v_s]
        self.step_accessed_nodes.add(u_s)
        if [u_s, v_s] not in self.visited_edges:
            self.visited_edges.append([u_s, v_s])

    def on_step_start(self):
        self.active_node = None
        self.step_accessed_nodes.clear()
        self.in_flight_nodes.clear()
        self.active_edge = None

    def on_line_fallback(self, loop_target_vars, frame_locals, all_frames_locals=None):
        self.pointer_vars.clear()
        for k, v in frame_locals.items():
            if isinstance(v, ListNode) and not k.startswith('_'):
                nid = str(v._id)
                self.pointer_vars[k] = nid
                if k != self.param_name:
                    self.in_flight_nodes.add(nid)
                if self.active_node is None and k != self.param_name:
                    self._record_node_access(v)
        if self.active_node is None and self.pointer_vars:
            first_nid = next(iter(self.pointer_vars.values()))
            if first_nid in self.all_nodes:
                self._record_node_access(self.all_nodes[first_nid])

        for f_loc in (all_frames_locals or []):
            for k, v in f_loc.items():
                if isinstance(v, ListNode) and not k.startswith('_') and k != self.param_name:
                    self.in_flight_nodes.add(str(v._id))

    def enhance_state_vars(self, state_vars):
        pass

    def on_return(self, ret_val):
        if isinstance(ret_val, ListNode):
            self.head = ret_val
        self.active_node = None
        self.active_edge = None
        self.step_accessed_nodes.clear()
        self.in_flight_nodes.clear()
        return self.snapshot(found_node=str(ret_val._id) if isinstance(ret_val, ListNode) else None)

    def snapshot(self, found_node=None):
        nodes_ordered = self._reachable_nodes()
        idx_map = {str(n._id): i for i, n in enumerate(nodes_ordered)}
        act_idx = idx_map.get(self.active_node, -1)
        fnd_idx = idx_map.get(found_node, -1) if found_node else -1

        nodes_out = []
        edges_out = []
        for n in nodes_ordered:
            nid = str(n._id)
            nodes_out.append({
                'id': nid,
                'val': _serialize(n._val),
                'next': str(n._next._id) if n._next else None,
                'prev': str(n._prev._id) if n._prev else None,
            })
            if n._next is not None:
                edges_out.append({'from': nid, 'to': str(n._next._id), 'type': 'next'})
            if self.is_doubly and n._prev is not None:
                edges_out.append({'from': nid, 'to': str(n._prev._id), 'type': 'prev'})

        active_nodes = [self.active_node] if self.active_node else []
        if self.active_edge:
            for ep in self.active_edge:
                if ep not in active_nodes:
                    active_nodes.append(ep)

        return _base_visual_dict(
            dsType=self.subtype,
            activeIndex=act_idx,
            foundIndex=fnd_idx,
            activeNodeId=self.active_node,
            activeNodeIds=active_nodes,
            foundNodeId=found_node,
            activeEdge=self.active_edge,
            visitedEdges=list(self.visited_edges),
            elements=[_serialize(n._val) for n in nodes_ordered],
            nodes=nodes_out,
            edges=edges_out,
            pointers=dict(self.pointer_vars),
            _accessed=list(self.step_accessed_nodes),
            _in_flight=list(self.in_flight_nodes),
        )

    def finalize_steps(self, trace_steps, is_paused_for_choice=False):
        _finalize_node_steps(trace_steps, is_paused_for_choice)

    def __getattr__(self, name):
        if self.head is not None and hasattr(self.head, name):
            return getattr(self.head, name)
        raise AttributeError(f"'VisualLinkedList' object has no attribute '{name}'")

    def __iter__(self):
        if self.head is None:
            return iter([])
        return iter(self.head)

    def __len__(self):
        return len(self._reachable_nodes())

    def __getitem__(self, idx):
        nodes = self._reachable_nodes()
        node = nodes[idx]
        self._record_node_access(node)
        return node._val


# ----------------------------------------------------------------------------
# 1C. TREES
# ----------------------------------------------------------------------------

class TreeNode:
    def __init__(self, val, node_id, owner, height=1):
        object.__setattr__(self, '_val', val)
        object.__setattr__(self, '_id', _NodeId(str(node_id)))
        object.__setattr__(self, '_left', None)
        object.__setattr__(self, '_right', None)
        object.__setattr__(self, '_parent', None)
        object.__setattr__(self, '_children', [])
        object.__setattr__(self, '_height', height)
        object.__setattr__(self, '_owner', owner)
        owner._register_node(self)

    @property
    def id(self): return self._id

    @property
    def val(self):
        self._owner._record_node_access(self)
        return self._val
    @val.setter
    def val(self, v):
        object.__setattr__(self, '_val', v)
        self._owner._record_node_access(self)

    @property
    def key(self): return self.val
    @key.setter
    def key(self, v): self.val = v
    @property
    def value(self): return self.val
    @value.setter
    def value(self, v): self.val = v

    @property
    def left(self):
        self._owner._record_node_access(self)
        if self._left is not None:
            self._owner._record_edge_access(self._id, self._left._id)
        return self._left
    @left.setter
    def left(self, node):
        object.__setattr__(self, '_left', node)
        if node is not None:
            object.__setattr__(node, '_parent', self)
            self._owner._record_edge_access(self._id, node._id)
        self._owner._sync_children(self)

    @property
    def right(self):
        self._owner._record_node_access(self)
        if self._right is not None:
            self._owner._record_edge_access(self._id, self._right._id)
        return self._right
    @right.setter
    def right(self, node):
        object.__setattr__(self, '_right', node)
        if node is not None:
            object.__setattr__(node, '_parent', self)
            self._owner._record_edge_access(self._id, node._id)
        self._owner._sync_children(self)

    @property
    def children(self):
        self._owner._record_node_access(self)
        if self._children:
            return self._children
        res = []
        if self._left is not None: res.append(self._left)
        if self._right is not None: res.append(self._right)
        return res
    @children.setter
    def children(self, ch_list):
        object.__setattr__(self, '_children', list(ch_list or []))
        for c in self._children:
            if isinstance(c, TreeNode):
                object.__setattr__(c, '_parent', self)

    @property
    def height(self): return self._height
    @height.setter
    def height(self, h): object.__setattr__(self, '_height', h)

    @property
    def root(self): return self._owner.root

    def __getitem__(self, key): return self._owner[key]
    def get(self, key, default=None): return self._owner.get(key, default)
    def __contains__(self, key): return key in self._owner

    def __repr__(self):
        return f"TreeNode({self._val!r})"


class VisualTree:
    def __init__(self, payload, param_name='root', subtype='binary_tree'):
        self.param_name = param_name
        self.subtype = subtype
        self.all_nodes = OrderedDict()
        self.root = None
        self.active_node = None
        self.active_edge = None
        self.visited_edges = []
        self.step_accessed_nodes = set()
        self.in_flight_nodes = set()
        self.pointer_vars = {}
        self._adj_fallback = {}
        self._build_from_payload(payload)

    def _register_node(self, node):
        self.all_nodes[str(node._id)] = node

    def _sync_children(self, node):
        ch = []
        if node._left is not None: ch.append(node._left)
        if node._right is not None: ch.append(node._right)
        object.__setattr__(node, '_children', ch)

    def _build_from_payload(self, payload):
        if payload is None:
            return
        if isinstance(payload, list):
            if not payload: return
            nodes = []
            for i, val in enumerate(payload):
                if val is None: nodes.append(None)
                else: nodes.append(TreeNode(val, str(i), self))
            for i, node in enumerate(nodes):
                if node is not None:
                    l_idx, r_idx = 2 * i + 1, 2 * i + 2
                    if l_idx < len(nodes) and nodes[l_idx] is not None:
                        object.__setattr__(node, '_left', nodes[l_idx])
                        object.__setattr__(nodes[l_idx], '_parent', node)
                    if r_idx < len(nodes) and nodes[r_idx] is not None:
                        object.__setattr__(node, '_right', nodes[r_idx])
                        object.__setattr__(nodes[r_idx], '_parent', node)
                    self._sync_children(node)
            self.root = nodes[0]
            return

        if isinstance(payload, dict) and any(k in payload for k in ('val', 'value', 'key', 'left', 'right', 'children', 'root')):
            root_data = payload.get('root', payload)
            counter = [0]
            def _build_rec(d):
                if d is None: return None
                if not isinstance(d, dict):
                    nid = str(counter[0])
                    counter[0] += 1
                    return TreeNode(d, nid, self)
                nid = str(d.get('id', counter[0]))
                counter[0] += 1
                val = d.get('val', d.get('value', d.get('key', d.get('label', nid))))
                h = d.get('height', 1)
                node = TreeNode(val, nid, self, height=h)
                if 'left' in d or 'right' in d:
                    l_node = _build_rec(d.get('left'))
                    r_node = _build_rec(d.get('right'))
                    object.__setattr__(node, '_left', l_node)
                    object.__setattr__(node, '_right', r_node)
                    if l_node: object.__setattr__(l_node, '_parent', node)
                    if r_node: object.__setattr__(r_node, '_parent', node)
                    self._sync_children(node)
                elif 'children' in d:
                    ch_nodes = [_build_rec(c) for c in d.get('children', []) if c is not None]
                    object.__setattr__(node, '_children', ch_nodes)
                    if len(ch_nodes) >= 1: object.__setattr__(node, '_left', ch_nodes[0])
                    if len(ch_nodes) >= 2: object.__setattr__(node, '_right', ch_nodes[1])
                return node
            self.root = _build_rec(root_data)
            return

        if isinstance(payload, dict):
            self._adj_fallback = payload
            node_map = {}
            has_parent = set()
            for k, children in payload.items():
                sk = str(k)
                lbl = _node_labels.get(sk, sk)
                if sk not in node_map: node_map[sk] = TreeNode(lbl, sk, self)
                for c in (children or []):
                    ck = str(c[0]) if isinstance(c, (list, tuple)) else str(c)
                    clbl = _node_labels.get(ck, ck)
                    if ck not in node_map: node_map[ck] = TreeNode(clbl, ck, self)
                    has_parent.add(ck)
            for k, children in payload.items():
                parent_node = node_map[str(k)]
                ch_nodes = [node_map[str(c[0]) if isinstance(c, (list, tuple)) else str(c)] for c in (children or [])]
                object.__setattr__(parent_node, '_children', ch_nodes)
                if len(ch_nodes) >= 1:
                    object.__setattr__(parent_node, '_left', ch_nodes[0])
                    object.__setattr__(ch_nodes[0], '_parent', parent_node)
                if len(ch_nodes) >= 2:
                    object.__setattr__(parent_node, '_right', ch_nodes[1])
                    object.__setattr__(ch_nodes[1], '_parent', parent_node)
            roots = [k for k in node_map.keys() if k not in has_parent]
            first_key = roots[0] if roots else (next(iter(node_map.keys())) if node_map else None)
            self.root = node_map.get(first_key)

    def _record_node_access(self, node):
        if node is None: return
        nid = str(node._id) if isinstance(node, TreeNode) else str(node)
        if nid in self.all_nodes:
            self.active_node = nid
            self.step_accessed_nodes.add(nid)

    def _record_edge_access(self, u_id, v_id):
        u_s, v_s = str(u_id), str(v_id)
        self.active_edge = [u_s, v_s]
        self.step_accessed_nodes.add(u_s)
        if [u_s, v_s] not in self.visited_edges:
            self.visited_edges.append([u_s, v_s])

    def __getitem__(self, key):
        s_key = str(key._id) if isinstance(key, TreeNode) else str(key)
        if s_key in self.all_nodes:
            node = self.all_nodes[s_key]
            self._record_node_access(node)
            ch_ids = [_NodeId(str(c._id)) for c in node.children]
            return _GraphNeighborList(self, s_key, ch_ids)
        raise KeyError(key)

    def _on_edge_inspect(self, u_key, v_entry):
        v_str = str(v_entry[0]) if isinstance(v_entry, tuple) else str(v_entry)
        self._record_node_access(u_key)
        self._record_edge_access(u_key, v_str)

    def get(self, key, default=None):
        try: return self[key]
        except KeyError: return default

    def __contains__(self, key):
        s_key = str(key._id) if isinstance(key, TreeNode) else str(key)
        return s_key in self.all_nodes

    def __iter__(self):
        for nid in self.all_nodes.keys():
            yield _NodeId(nid)

    def keys(self):
        return [_NodeId(nid) for nid in self.all_nodes.keys()]

    def on_step_start(self):
        self.active_node = None
        self.step_accessed_nodes.clear()
        self.in_flight_nodes.clear()
        self.active_edge = None

    def on_line_fallback(self, loop_target_vars, frame_locals, all_frames_locals=None):
        self.pointer_vars.clear()
        for k, v in frame_locals.items():
            if isinstance(v, TreeNode) and not k.startswith('_'):
                nid = str(v._id)
                self.pointer_vars[k] = nid
                self.in_flight_nodes.add(nid)
                if self.active_node is None:
                    self._record_node_access(v)
            elif isinstance(v, _NodeId) and str(v) in self.all_nodes:
                nid = str(v)
                self.in_flight_nodes.add(nid)
                if self.active_node is None:
                    self._record_node_access(nid)

        for f_loc in (all_frames_locals or []):
            for k, v in f_loc.items():
                if k.startswith('_'): continue
                if isinstance(v, TreeNode):
                    self.in_flight_nodes.add(str(v._id))
                elif isinstance(v, _NodeId) and str(v) in self.all_nodes:
                    self.in_flight_nodes.add(str(v))

    def enhance_state_vars(self, state_vars):
        pass

    def on_return(self, ret_val):
        if isinstance(ret_val, TreeNode):
            self.root = ret_val
        self.active_node = None
        self.active_edge = None
        self.step_accessed_nodes.clear()
        self.in_flight_nodes.clear()
        found_id = str(ret_val._id) if isinstance(ret_val, TreeNode) else None
        return self.snapshot(found_node=found_id)

    def snapshot(self, found_node=None):
        nodes_out = []
        edges_out = []
        for nid, n in self.all_nodes.items():
            l_id = str(n._left._id) if n._left else None
            r_id = str(n._right._id) if n._right else None
            lh = n._left._height if n._left else 0
            rh = n._right._height if n._right else 0
            nodes_out.append({
                'id': nid, 'val': _serialize(n._val), 'left': l_id, 'right': r_id,
                'height': n._height, 'balanceFactor': lh - rh,
                'children': [str(c._id) for c in n.children],
            })
            for c in n.children:
                edges_out.append({'from': nid, 'to': str(c._id)})

        active_nodes = [self.active_node] if self.active_node else []
        if self.active_edge:
            for ep in self.active_edge:
                if ep not in active_nodes: active_nodes.append(ep)

        return _base_visual_dict(
            dsType=self.subtype,
            activeNodeId=self.active_node,
            activeNodeIds=active_nodes,
            foundNodeId=found_node,
            activeEdge=self.active_edge,
            visitedEdges=list(self.visited_edges),
            rootId=str(self.root._id) if self.root else None,
            nodes=nodes_out, edges=edges_out, pointers=dict(self.pointer_vars),
            _accessed=list(self.step_accessed_nodes),
            _in_flight=list(self.in_flight_nodes),
        )

    def finalize_steps(self, trace_steps, is_paused_for_choice=False):
        _finalize_node_steps(trace_steps, is_paused_for_choice)

    def __getattr__(self, name):
        if self.root is not None and hasattr(self.root, name):
            return getattr(self.root, name)
        raise AttributeError(f"'VisualTree' object has no attribute '{name}'")


# ----------------------------------------------------------------------------
# 1D. GRAPHS
# ----------------------------------------------------------------------------

class _GraphNeighborDict(dict):
    def __init__(self, graph, source_key, neighbor_pairs):
        super().__init__(neighbor_pairs)
        self._graph = graph
        self._source = str(source_key)

    def __getitem__(self, v_key):
        sv = _NodeId(str(v_key))
        w = super().__getitem__(sv)
        self._graph._on_edge_inspect(self._source, (sv, w))
        return w

    def items(self):
        pair_list = list(super().items())
        return _GraphNeighborList(self._graph, self._source, pair_list)

    def keys(self):
        key_list = list(super().keys())
        return _GraphNeighborList(self._graph, self._source, key_list)

    def __iter__(self):
        return iter(self.keys())


class _GraphNeighborList(list):
    def __init__(self, graph, source_key, neighbors):
        super().__init__(neighbors)
        self._graph = graph
        self._source = str(source_key)

    def _iterate_items(self, items_list):
        if _sim_mode != 'manual':
            for nb in items_list:
                self._graph._on_edge_inspect(self._source, nb)
                yield nb
            self._graph.active_edge = None
            return

        remaining = list(items_list)
        while remaining:
            if len(remaining) > 1:
                src_label = _node_labels.get(self._source, self._source)
                candidates = []
                for nb in remaining:
                    nb_id = str(nb[0]) if isinstance(nb, tuple) else str(nb)
                    weight = nb[1] if isinstance(nb, tuple) and len(nb) > 1 else None
                    nb_label = _node_labels.get(nb_id, nb_id)
                    edge_lbl = f"{src_label} → {nb_label}" + (f" (w={weight})" if weight is not None else "")
                    candidates.append({
                        'id': nb_id, 'label': nb_label, 'weight': weight,
                        'edge': [self._source, nb_id], 'edgeLabel': edge_lbl, '_raw': nb,
                    })

                if _user_choices:
                    chosen_id = str(_user_choices.pop(0))
                    match_idx = next((i for i, c in enumerate(candidates) if c['id'] == chosen_id), 0)
                    nb = remaining.pop(match_idx)
                else:
                    clean_candidates = [{k: v for k, v in c.items() if k != '_raw'} for c in candidates]
                    raise _WaitForUserChoice({
                        'type': 'select_neighbor', 'sourceNodeId': self._source,
                        'candidateNodeIds': [c['id'] for c in clean_candidates],
                        'candidateEdges': [c['edge'] for c in clean_candidates],
                        'candidates': clean_candidates,
                        'title': f"Choose the next neighbor of '{src_label}' to inspect",
                        'reason': f"Node '{src_label}' has {len(clean_candidates)} remaining incident edges. Select one:"
                    })
            else:
                nb = remaining.pop(0)

            self._graph._on_edge_inspect(self._source, nb)
            yield nb

        self._graph.active_edge = None

    def __iter__(self): return self._iterate_items(super().__iter__())
    def __reversed__(self): return self._iterate_items(super().__reversed__())


class VisualGraph(dict):
    def __init__(self, raw_adj):
        self.edge_weights = {}
        self._is_dict_of_dicts = False
        wrapped = {}

        if isinstance(raw_adj, dict):
            for k, neighbors in raw_adj.items():
                uk = _NodeId(str(k))
                if isinstance(neighbors, dict):
                    self._is_dict_of_dicts = True
                    nb_pairs = []
                    for vk, w in neighbors.items():
                        v_node = _NodeId(str(vk))
                        nb_pairs.append((v_node, w))
                        self.edge_weights[f"{uk}->{v_node}"] = w
                    wrapped[uk] = nb_pairs
                else:
                    nb_list = []
                    for nb in (neighbors or []):
                        if isinstance(nb, dict):
                            target = nb.get('to', nb.get('node', nb.get('id', nb.get('target'))))
                            w = nb.get('weight', nb.get('cost', nb.get('w')))
                            v_node = _NodeId(str(target))
                            if w is not None:
                                nb_list.append((v_node, w))
                                self.edge_weights[f"{uk}->{v_node}"] = w
                            else: nb_list.append(v_node)
                        elif isinstance(nb, (list, tuple)) and len(nb) >= 2:
                            v_node = _NodeId(str(nb[0]))
                            w = nb[1]
                            nb_list.append((v_node, w))
                            self.edge_weights[f"{uk}->{v_node}"] = w
                        else: nb_list.append(_NodeId(str(nb)))
                    wrapped[uk] = nb_list

        super().__init__(wrapped)
        self.active_node = None
        self._discovered_nodes = set()
        self.active_edge = None
        self.active_edge_weight = None
        self.visited_edges = []
        self.step_accessed_nodes = set()
        self.in_flight_nodes = set()

    def on_step_start(self):
        self.active_node = None
        self.step_accessed_nodes.clear()
        self.in_flight_nodes.clear()

    def record_visit(self, node_key):
        s_key = str(node_key)
        if s_key not in self: return
        self.active_node = s_key
        self.step_accessed_nodes.add(s_key)
        self._discovered_nodes.add(s_key)

    def _on_edge_inspect(self, u_key, v_entry):
        u_str = str(u_key)
        if isinstance(v_entry, tuple):
            v_str = str(v_entry[0])
            self.active_edge_weight = v_entry[1] if len(v_entry) > 1 else None
        else:
            v_str = str(v_entry)
            self.active_edge_weight = self.edge_weights.get(f"{u_str}->{v_str}")
        # Record u_str as actively expanded, and highlight edge (u_str, v_str),
        # without falsely marking v_str as expanded yet.
        self.record_visit(u_str)
        self.active_edge = [u_str, v_str]

    def _promote_discovered_edges(self, frame_locals):
        if not self.active_edge: return
        u_str, v_str = self.active_edge

        for var_name, val in frame_locals.items():
            if var_name.startswith('_') or val is self:
                continue
            if isinstance(val, (list, tuple, set, deque)):
                for item in val:
                    item_id = str(item[-1]) if isinstance(item, (list, tuple)) and item else str(item)
                    if item_id == v_str or str(item) == v_str:
                        self._discovered_nodes.add(v_str)
                        break
            elif isinstance(val, dict):
                if str(v_str) in val:
                    self._discovered_nodes.add(v_str)

        if v_str in self._discovered_nodes:
            pair = [u_str, v_str]
            if pair not in self.visited_edges:
                self.visited_edges.append(pair)

    def __getitem__(self, key):
        s_key = _NodeId(str(key))
        if s_key in self:
            self.record_visit(s_key)
            raw_neighbors = super().__getitem__(s_key)
            if self._is_dict_of_dicts: return _GraphNeighborDict(self, s_key, raw_neighbors)
            return _GraphNeighborList(self, s_key, raw_neighbors)
        return super().__getitem__(key)

    def get(self, key, default=None):
        s_key = _NodeId(str(key))
        if s_key in self: return self[s_key]
        return default

    # Passive iterations and lookups DO NOT trigger node visits
    def __contains__(self, key):
        s_key = _NodeId(str(key))
        return super().__contains__(s_key)

    def __iter__(self):
        for k in super().__iter__():
            yield _NodeId(k)

    def keys(self):
        return [_NodeId(k) for k in super().keys()]

    def items(self):
        return [(_NodeId(k), super().__getitem__(k)) for k in super().keys()]

    def on_line_fallback(self, loop_target_vars, frame_locals, all_frames_locals=None):
        # 1. If a loop variable is a node (e.g., `for neighbor in graph[u]:`),
        # keep the source node `u` active if we are inspecting its edge, otherwise record loop target
        if self.active_edge and self.active_node is None:
            self.record_visit(self.active_edge[0])

        if self.active_node is None:
            for val in loop_target_vars:
                if isinstance(val, _NodeId) and str(val) in self:
                    self.record_visit(str(val))
                    break
                elif isinstance(val, tuple):
                    for sub in val:
                        if isinstance(sub, _NodeId) and str(sub) in self:
                            self.record_visit(str(sub))
                            break

        # 2. Check current frame scalar variables (e.g. `node`, `curr`, `u`) when backtracking
        if self.active_node is None:
            for k, val in frame_locals.items():
                if k.startswith('_') or val is self:
                    continue
                if isinstance(val, _NodeId) and str(val) in self:
                    self.record_visit(str(val))
                    break

        # 3. Track all nodes currently held in any call-stack frame (e.g. parent recursive calls)
        # or active frontier queues/stacks so they are never marked completely visited prematurely.
        for f_loc in (all_frames_locals or [frame_locals]):
            for k, val in f_loc.items():
                if k.startswith('_') or val is self:
                    continue
                if isinstance(val, _NodeId) and str(val) in self:
                    self.in_flight_nodes.add(str(val))
                elif isinstance(val, (list, deque)):
                    for item in val:
                        if isinstance(item, _NodeId) and str(item) in self:
                            self.in_flight_nodes.add(str(item))
                        elif isinstance(item, tuple):
                            for sub in item:
                                if isinstance(sub, _NodeId) and str(sub) in self:
                                    self.in_flight_nodes.add(str(sub))

        self._promote_discovered_edges(frame_locals)

    def enhance_state_vars(self, state_vars): pass

    def on_return(self, ret_val):
        self.active_node = None
        self.active_edge = None
        self.step_accessed_nodes.clear()
        self.in_flight_nodes.clear()
        return self.snapshot()

    def snapshot(self):
        active_nodes = []
        if self.active_node is not None: active_nodes.append(self.active_node)
        if self.active_edge:
            for endpoint in self.active_edge:
                if endpoint not in active_nodes: active_nodes.append(endpoint)
        return _base_visual_dict(
            dsType='graph', activeNodeId=self.active_node, activeNodeIds=active_nodes,
            foundNodeId=None, visitedNodes=[], activeEdge=self.active_edge,
            activeEdgeWeight=_serialize(self.active_edge_weight),
            visitedEdges=list(self.visited_edges),
            edgeWeights={k: _serialize(v) for k, v in self.edge_weights.items()},
            _accessed=list(self.step_accessed_nodes),
            _in_flight=list(self.in_flight_nodes),
        )

    def finalize_steps(self, trace_steps, is_paused_for_choice=False):
        _finalize_node_steps(trace_steps, is_paused_for_choice)


# ----------------------------------------------------------------------------
# 1E. 2D MATRIX / GRID
# ----------------------------------------------------------------------------

class _MatrixRow(list):
    def __init__(self, matrix, row_idx, iterable):
        super().__init__(iterable)
        self._matrix = matrix
        self._row_idx = row_idx

    def __getitem__(self, col_idx):
        if isinstance(col_idx, int) and not isinstance(col_idx, bool):
            norm_c = col_idx if col_idx >= 0 else len(self) + col_idx
            if 0 <= norm_c < len(self):
                self._matrix._record_cell(self._row_idx, norm_c)
        return super().__getitem__(col_idx)

    def __setitem__(self, col_idx, val):
        super().__setitem__(col_idx, val)
        if isinstance(col_idx, int) and not isinstance(col_idx, bool):
            norm_c = col_idx if col_idx >= 0 else len(self) + col_idx
            if 0 <= norm_c < len(self):
                self._matrix._record_cell(self._row_idx, norm_c)


class VisualMatrix(list):
    def __init__(self, grid_data, param_name='matrix'):
        rows = [_MatrixRow(self, r, row) for r, row in enumerate(grid_data or [])]
        super().__init__(rows)
        self.param_name = param_name
        self.active_cell = None
        self.recent_accesses = {}
        self.step_accessed_cells = set()
        self.in_flight_cells = set()

    def _record_cell(self, r, c):
        self.active_cell = [r, c]
        self.step_accessed_cells.add((r, c))
        val = list.__getitem__(list.__getitem__(self, r), c)
        self.recent_accesses[f"{self.param_name}[{r}][{c}]"] = val

    def on_step_start(self):
        self.active_cell = None
        self.recent_accesses.clear()
        self.step_accessed_cells.clear()
        self.in_flight_cells.clear()

    def on_line_fallback(self, loop_target_vars, frame_locals, all_frames_locals=None):
        if not self.recent_accesses and len(loop_target_vars) >= 2:
            r, c = loop_target_vars[0], loop_target_vars[1]
            if isinstance(r, int) and not isinstance(r, bool) and isinstance(c, int) and not isinstance(c, bool):
                if 0 <= r < len(self) and 0 <= c < len(self[r]):
                    self._record_cell(r, c)

        for f_loc in (all_frames_locals or [frame_locals]):
            for r_key, c_key in (('r', 'c'), ('row', 'col'), ('i', 'j'), ('x', 'y')):
                if r_key in f_loc and c_key in f_loc:
                    r, c = f_loc[r_key], f_loc[c_key]
                    if isinstance(r, int) and not isinstance(r, bool) and isinstance(c, int) and not isinstance(c, bool):
                        if 0 <= r < len(self) and 0 <= c < len(self[r]):
                            self.in_flight_cells.add((r, c))
                            if self.active_cell is None and f_loc is frame_locals:
                                self._record_cell(r, c)

    def enhance_state_vars(self, state_vars):
        for expr_str, val in self.recent_accesses.items():
            state_vars[expr_str] = _serialize(val)

    def on_return(self, ret_val):
        found_cell = None
        if isinstance(ret_val, (list, tuple)) and len(ret_val) == 2 and all(isinstance(x, int) for x in ret_val):
            found_cell = [ret_val[0], ret_val[1]]
        self.active_cell = None
        self.step_accessed_cells.clear()
        self.in_flight_cells.clear()
        return self.snapshot(found_cell)

    def snapshot(self, found_cell=None):
        cols = len(self[0]) if len(self) > 0 else 0
        flat_active = self.active_cell[0] * cols + self.active_cell[1] if self.active_cell and cols else -1
        flat_found = found_cell[0] * cols + found_cell[1] if found_cell and cols else -1
        return _base_visual_dict(
            dsType='matrix', activeIndex=flat_active, foundIndex=flat_found,
            activeCell=found_cell if found_cell else self.active_cell,
            foundCell=found_cell, checkedCells=[],
            grid=[[_serialize(cell) for cell in row] for row in self],
            _accessed=[list(c) for c in self.step_accessed_cells],
            _in_flight=[list(c) for c in self.in_flight_cells],
        )

    def finalize_steps(self, trace_steps, is_paused_for_choice=False):
        last_step = {}
        first_step = {}
        for idx, step in enumerate(trace_steps):
            vis = step['visual']
            accessed = [tuple(x) for x in vis.pop('_accessed', [])]
            in_flight = [tuple(x) for x in vis.pop('_in_flight', [])]
            if vis.get('activeCell'):
                ac = tuple(vis['activeCell'])
                if ac not in accessed: accessed.append(ac)
            for cell in accessed:
                if cell not in first_step: first_step[cell] = idx
                last_step[cell] = idx
            for cell in in_flight:
                if cell in first_step:
                    last_step[cell] = max(last_step.get(cell, idx), idx)

        ordered = sorted(first_step.keys(), key=lambda c: first_step[c])
        for idx, step in enumerate(trace_steps):
            vis = step['visual']
            ac = tuple(vis['activeCell']) if vis.get('activeCell') else None
            fc = tuple(vis['foundCell']) if vis.get('foundCell') else None
            vis['checkedCells'] = [
                list(c) for c in ordered
                if first_step[c] < idx and last_step[c] < idx and c != ac and c != fc
            ]


# ----------------------------------------------------------------------------
# 1F. HASH STRUCTURES & CACHE STRUCTURES
# ----------------------------------------------------------------------------

class VisualHash:
    def __init__(self, payload, param_name='hash_map', subtype='hash_map'):
        self.param_name = param_name
        self.subtype = subtype
        self.is_set = subtype == 'hash_set'
        self.is_lru = subtype in ('lru_cache', 'cache_structures')
        self.capacity = None
        self._store = OrderedDict()

        if isinstance(payload, dict):
            if 'capacity' in payload and ('entries' in payload or 'items' in payload or self.is_lru):
                self.capacity = int(payload.get('capacity', 4))
                raw_items = payload.get('entries', payload.get('items', {}))
                if isinstance(raw_items, dict):
                    self._store.update(raw_items)
                elif isinstance(raw_items, list):
                    for pair in raw_items:
                        if isinstance(pair, (list, tuple)) and len(pair) >= 2:
                            self._store[pair[0]] = pair[1]
            else:
                self._store.update(payload)
        elif isinstance(payload, list):
            if self.is_set:
                for x in payload: self._store[x] = True
            else:
                for i, item in enumerate(payload):
                    if isinstance(item, (list, tuple)) and len(item) >= 2:
                        self._store[item[0]] = item[1]
                    else: self._store[i] = item

        if self.is_lru and self.capacity is None:
            self.capacity = max(4, len(self._store))

        self.active_key = None
        self.evicted_key = None
        self.cache_status = None
        self.recent_accesses = {}
        self.step_accessed_keys = set()
        self.in_flight_keys = set()

    def _record_key(self, key, val=None, status=None):
        s_key = str(_serialize(key))
        self.active_key = s_key
        self.step_accessed_keys.add(s_key)
        if status: self.cache_status = status
        if not self.is_set and val is not None:
            self.recent_accesses[f"{self.param_name}[{key!r}]"] = val

    def __getitem__(self, key):
        if key in self._store:
            val = self._store[key]
            if self.is_lru: self._store.move_to_end(key)
            self._record_key(key, val, status='HIT')
            return val
        self._record_key(key, None, status='MISS')
        raise KeyError(key)

    def __setitem__(self, key, val):
        if key in self._store:
            if self.is_lru: self._store.move_to_end(key)
            self._store[key] = val
            self._record_key(key, val, status='PUT')
            return
        if self.is_lru and self.capacity and len(self._store) >= self.capacity:
            old_k, _ = self._store.popitem(last=False)
            self.evicted_key = str(_serialize(old_k))
        self._store[key] = val
        self._record_key(key, val, status='PUT')

    def get(self, key, default=-1 if 'lru' in _NORM_CATEGORY else None):
        if key in self._store: return self[key]
        self._record_key(key, default, status='MISS')
        return default

    def put(self, key, val): self[key] = val
    def add(self, key):
        self._store[key] = True
        self._record_key(key, True, status='ADD')
    def remove(self, key):
        self._record_key(key, status='REMOVE')
        del self._store[key]
    def discard(self, key):
        self._record_key(key, status='REMOVE')
        self._store.pop(key, None)
    def pop(self, *args):
        if not args and self.is_set:
            k, _ = self._store.popitem()
            self._record_key(k, status='REMOVE')
            return k
        k = args[0]
        self._record_key(k, status='REMOVE')
        return self._store.pop(*args)
    def __delitem__(self, key):
        self._record_key(key, status='REMOVE')
        del self._store[key]

    # Passive membership check should not trigger visited state
    def __contains__(self, key):
        return key in self._store

    def keys(self): return list(self._store.keys())
    def values(self): return list(self._store.values()) if not self.is_set else list(self._store.keys())
    def items(self): return list(self._store.items())

    # Passive iteration should not mark all items as visited
    def __iter__(self):
        return iter(self._store)

    def __len__(self): return len(self._store)

    def on_step_start(self):
        self.active_key = None
        self.recent_accesses.clear()
        self.step_accessed_keys.clear()
        self.in_flight_keys.clear()
        self.evicted_key = None
        self.cache_status = None

    def on_line_fallback(self, loop_target_vars, frame_locals, all_frames_locals=None):
        if self.active_key is None:
            for val in loop_target_vars:
                if isinstance(val, (int, str, float, tuple)) and val in self._store:
                    self._record_key(val, self._store.get(val))
                    break

    def enhance_state_vars(self, state_vars):
        for expr_str, val in self.recent_accesses.items():
            state_vars[expr_str] = _serialize(val)

    def on_return(self, ret_val):
        self.active_key = None
        self.step_accessed_keys.clear()
        self.in_flight_keys.clear()
        return self.snapshot()

    def snapshot(self):
        entries = [{'key': str(_serialize(k)), 'value': None if self.is_set else _serialize(v)} for k, v in self._store.items()]
        if self.is_lru: entries = list(reversed(entries))
        return _base_visual_dict(
            dsType=self.subtype, activeNodeId=self.active_key,
            activeNodeIds=[self.active_key] if self.active_key else [],
            activeKey=self.active_key, evictedKey=self.evicted_key,
            cacheStatus=self.cache_status, capacity=self.capacity,
            entries=entries, elements=[e['key'] if self.is_set else f"{e['key']}: {e['value']}" for e in entries],
            _accessed=list(self.step_accessed_keys),
            _in_flight=list(self.in_flight_keys),
        )

    def finalize_steps(self, trace_steps, is_paused_for_choice=False):
        _finalize_node_steps(trace_steps, is_paused_for_choice)


# ============================================================================
# 2. COMPLETE 29-DATA-STRUCTURE REGISTRY
# ============================================================================

_PROXY_REGISTRY = {
    'sequence': lambda p, fn: VisualSequence(p, fn, 'array'),
    'array': lambda p, fn: VisualSequence(p, fn, 'array'),
    'string': lambda p, fn: VisualSequence(p, fn, 'string'),
    'stack': lambda p, fn: VisualSequence(p, fn, 'stack'),
    'queue': lambda p, fn: VisualSequence(p, fn, 'queue'),
    'circular_queue': lambda p, fn: VisualSequence(p, fn, 'circular_queue'),
    'deque': lambda p, fn: VisualSequence(p, fn, 'deque'),
    'priority_queue': lambda p, fn: VisualSequence(p, fn, 'priority_queue'),
    'heap': lambda p, fn: VisualSequence(p, fn, 'heap'),
    'binary_heap': lambda p, fn: VisualSequence(p, fn, 'binary_heap'),
    'min_heap': lambda p, fn: VisualSequence(p, fn, 'min_heap'),
    'max_heap': lambda p, fn: VisualSequence(p, fn, 'max_heap'),
    'linked_list': lambda p, fn: VisualLinkedList(p, fn, 'linked_list'),
    'singly_linked_list': lambda p, fn: VisualLinkedList(p, fn, 'singly_linked_list'),
    'doubly_linked_list': lambda p, fn: VisualLinkedList(p, fn, 'doubly_linked_list'),
    'circular_linked_list': lambda p, fn: VisualLinkedList(p, fn, 'circular_linked_list'),
    'circular_singly_linked_list': lambda p, fn: VisualLinkedList(p, fn, 'circular_singly_linked_list'),
    'circular_doubly_linked_list': lambda p, fn: VisualLinkedList(p, fn, 'circular_doubly_linked_list'),
    'tree': lambda p, fn: VisualTree(p, fn, 'tree'),
    'binary_tree': lambda p, fn: VisualTree(p, fn, 'binary_tree'),
    'binary_search_tree': lambda p, fn: VisualTree(p, fn, 'binary_search_tree'),
    'avl_tree': lambda p, fn: VisualTree(p, fn, 'avl_tree'),
    'graph': lambda p, fn: VisualGraph(p),
    'matrix': lambda p, fn: VisualMatrix(p, fn),
    'hash_based_structures': lambda p, fn: VisualHash(p, fn, 'hash_table'),
    'hash_table': lambda p, fn: VisualHash(p, fn, 'hash_table'),
    'hash_map': lambda p, fn: VisualHash(p, fn, 'hash_map'),
    'hash_set': lambda p, fn: VisualHash(p, fn, 'hash_set'),
    'cache_structures': lambda p, fn: VisualHash(p, fn, 'cache_structures'),
    'lru_cache': lambda p, fn: VisualHash(p, fn, 'lru_cache'),
}


def _serialize(v, _depth=0):
    if _depth > 6: return "..."
    if isinstance(v, _NodeId): return _node_labels.get(str(v), str(v))
    if isinstance(v, (ListNode, TreeNode)): return f"Node({_serialize(v._val, _depth + 1)})"
    if isinstance(v, (VisualLinkedList, VisualTree)): return repr(v.head if hasattr(v, 'head') else v.root)
    if isinstance(v, bool) or v is None: return v
    if isinstance(v, float):
        if math.isinf(v): return "∞" if v > 0 else "-∞"
        if math.isnan(v): return "NaN"
        return round(v, 4) if v != int(v) else int(v)
    if isinstance(v, (int, str)): return v
    if isinstance(v, (list, tuple, set, deque)): return [_serialize(x, _depth + 1) for x in v]
    if isinstance(v, (dict, VisualHash)):
        items = v.items()
        return {str(_serialize(k, _depth + 1)): _serialize(val, _depth + 1) for k, val in items}
    return repr(v)


def _build_loop_target_names(code_str):
    line_map = {}
    try:
        tree = ast.parse(code_str)
        for node in ast.walk(tree):
            if isinstance(node, (ast.For, ast.AsyncFor)) and hasattr(node, 'lineno'):
                names = [sub.id for sub in ast.walk(node.target) if isinstance(sub, ast.Name) and isinstance(sub.ctx, ast.Store)]
                if names: line_map.setdefault(node.lineno, []).extend(names)
    except Exception: pass
    return line_map


def _extract_algo_line(exc_tb):
    tb_list = traceback.extract_tb(exc_tb)
    for frame_summary in reversed(tb_list):
        if frame_summary.filename == '<algorithm>':
            return frame_summary.lineno
    return _trace_steps[-1]['line'] if _trace_steps else None


try:
    _ns = {
        'choose': choose, 'ListNode': ListNode, 'TreeNode': TreeNode,
        'deque': deque, 'heapq': heapq, 'math': math,
    }
    exec(compile(_user_code, '<algorithm>', 'exec'), _ns)

    if _func_name not in _ns:
        raise NameError(f"Function '{_func_name}' was not found in the algorithm file.")

    _fn = _ns[_func_name]
    _sig_params = list(inspect.signature(_fn).parameters.keys())
    _param_names = set(_sig_params)
    _first_param = _sig_params[0] if _sig_params else 'data'
    _loop_targets = _build_loop_target_names(_user_code)

    _factory = _PROXY_REGISTRY.get(_NORM_CATEGORY, _PROXY_REGISTRY['sequence'])
    _visual_ds = _factory(_payload, _first_param)

    _raw_kwargs = json.loads(_raw_kwargs_json)
    _eval_kwargs = {}
    for _k, _v_str in _raw_kwargs.items():
        try: _val = ast.literal_eval(_v_str)
        except (ValueError, SyntaxError): _val = _v_str
        if _NORM_CATEGORY in ('graph', 'tree', 'binary_tree', 'binary_search_tree', 'avl_tree') and _val is not None:
            _s = str(_val).strip()
            if _s in _label_to_key: _val = _NodeId(_label_to_key[_s])
        _eval_kwargs[_k] = _val

    def _build_state_vars_and_callstack(frame, executed_lineno):
        curr_f = frame
        frames_chain = []
        while curr_f is not None and curr_f.f_code.co_filename == '<algorithm>':
            frames_chain.append(curr_f)
            curr_f = curr_f.f_back

        call_stack = []
        all_frames_locals = []
        merged_loc = {}
        for f_item in reversed(frames_chain):
            merged_loc.update(f_item.f_locals)
            all_frames_locals.append(f_item.f_locals)
            f_args = {k: _serialize(v) for k, v in f_item.f_locals.items() if not k.startswith('_') and k != _first_param and not inspect.isfunction(v) and not inspect.ismodule(v)}
            call_stack.append({'func': f_item.f_code.co_name, 'line': f_item.f_lineno, 'locals': f_args})

        current_frame_locals = frame.f_locals
        loop_var_names = _loop_targets.get(executed_lineno, [])
        loop_var_vals = [current_frame_locals[name] for name in loop_var_names if name in current_frame_locals and name not in _param_names]
        _visual_ds.on_line_fallback(loop_var_vals, current_frame_locals, all_frames_locals)

        state_vars = {}
        for k, v in merged_loc.items():
            if not k.startswith('_') and k != _first_param and not inspect.isfunction(v) and not inspect.ismodule(v):
                state_vars[k] = _serialize(v)

        _visual_ds.enhance_state_vars(state_vars)
        return state_vars, call_stack

    def _capture_snapshot_with_stack(call_stack, custom_visual=None):
        vis = custom_visual if custom_visual is not None else _visual_ds.snapshot()
        vis['callStack'] = call_stack
        vis['recursionDepth'] = max(0, len(call_stack) - 1)
        return vis

    def _tracer(frame, event, arg):
        global _step_count
        if frame.f_code.co_filename != '<algorithm>': return _tracer
        if event not in ('call', 'line', 'return'): return _tracer

        _step_count += 1
        if _step_count > _MAX_STEPS:
            raise _StepLimitExceeded(f"Execution exceeded {_MAX_STEPS} steps (possible infinite loop).")

        if event == 'call':
            caller = frame.f_back
            if caller is not None and caller.f_code.co_filename == '<algorithm>':
                caller_fid = id(caller)
                caller_pending = _pending_steps.pop(caller_fid, None)
                if caller_pending is not None:
                    caller_state, caller_stack = _build_state_vars_and_callstack(caller, caller_pending['line'])
                    _trace_steps.append({
                        'event': 'line', 'line': caller_pending['line'],
                        'stateVars': caller_state, 'visual': _capture_snapshot_with_stack(caller_stack),
                    })
                    _visual_ds.on_step_start()
            return _tracer

        fid = id(frame)
        pending = _pending_steps.pop(fid, None)
        executed_line = pending['line'] if pending is not None else frame.f_lineno

        state_vars, call_stack = _build_state_vars_and_callstack(frame, executed_line)

        if pending is not None and not (event == 'return' and pending['line'] == frame.f_lineno):
            _trace_steps.append({
                'event': 'line', 'line': pending['line'],
                'stateVars': state_vars, 'visual': _capture_snapshot_with_stack(call_stack),
            })

        if event == 'line':
            _visual_ds.on_step_start()
            _pending_steps[fid] = {'line': frame.f_lineno}
        else:
            if frame.f_code.co_name == _func_name and len(call_stack) <= 1:
                ret_val = _serialize(arg)
                ret_state_vars = dict(state_vars)
                ret_state_vars['return'] = ret_val
                final_visual = _visual_ds.on_return(arg)
                _trace_steps.append({
                    'event': 'return', 'line': frame.f_lineno,
                    'stateVars': ret_state_vars, 'visual': _capture_snapshot_with_stack(call_stack, final_visual),
                })
            else:
                _visual_ds.on_step_start()

        return _tracer

    _old_rec_limit = sys.getrecursionlimit()
    sys.setrecursionlimit(250)

    _arg_ds = _visual_ds
    if isinstance(_visual_ds, VisualLinkedList) and _visual_ds.head is not None:
        _arg_ds = _visual_ds.head
    elif isinstance(_visual_ds, VisualTree) and _visual_ds.root is not None and not _visual_ds._adj_fallback:
        _arg_ds = _visual_ds.root

    sys.settrace(_tracer)
    try:
        _fn(_arg_ds, **_eval_kwargs)
    finally:
        sys.settrace(None)
        sys.setrecursionlimit(_old_rec_limit)

    _visual_ds.finalize_steps(_trace_steps)

except _WaitForUserChoice as pause_exc:
    _visual_ds.finalize_steps(_trace_steps, is_paused_for_choice=True)
    if _trace_steps: _trace_steps[-1]['interaction'] = pause_exc.interaction
except _StepLimitExceeded as e:
    _visual_ds.finalize_steps(_trace_steps)
    _error_info = {'type': 'InfiniteLoopError', 'message': str(e), 'line': _trace_steps[-1]['line'] if _trace_steps else 1}
except RecursionError:
    _visual_ds.finalize_steps(_trace_steps)
    _, _, _tb = sys.exc_info()
    _error_info = {'type': 'RecursionError', 'message': 'Maximum recursion depth exceeded.', 'line': _extract_algo_line(_tb)}
except SyntaxError as e:
    _error_info = {'type': 'SyntaxError', 'message': f"{e.msg} (line {e.lineno})", 'line': e.lineno}
except Exception as e:
    if '_visual_ds' in locals(): _visual_ds.finalize_steps(_trace_steps)
    _, _, _tb = sys.exc_info()
    _error_info = {'type': type(e).__name__, 'message': str(e), 'line': _extract_algo_line(_tb)}

json.dumps({'steps': _trace_steps, 'error': _error_info})