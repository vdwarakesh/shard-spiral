# python/pyodide-worker.py
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

class _WaitForUserChoice(Exception):
    def __init__(self, interaction):
        self.interaction = interaction

_payload = json.loads(_ds_payload_json)
_node_labels = json.loads(_node_labels_json)
_user_choices = list(json.loads(_user_choices_json))

_label_to_key = {}
for _k in _node_labels.keys():
    _label_to_key[str(_k)] = str(_k)
for _k, _lbl in _node_labels.items():
    _label_to_key[str(_lbl)] = str(_k)

# Load the data-structure-specific Python proxy (e.g. sequence.py or graph.py)
exec(compile(_ds_proxy_code, '<ds_proxy>', 'exec'), globals())


def _serialize(v):
    if '_NodeId' in globals() and isinstance(v, _NodeId):
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


def _parse_arg_value(v_str):
    try:
        val = ast.literal_eval(v_str)
    except (ValueError, SyntaxError):
        val = v_str
    if val is not None and '_NodeId' in globals():
        s = str(val).strip()
        if s in _label_to_key:
            val = _NodeId(_label_to_key[s])
    return val


try:
    _ns = {}
    exec(compile(_user_code, '<algorithm>', 'exec'), _ns)

    _loop_targets, _assign_targets, _while_lines, _top_level_funcs = _build_ast_line_info(_user_code)

    if (_func_name not in _ns or _func_name.startswith('__')) and _top_level_funcs:
        _func_name = _top_level_funcs[0]

    if _func_name not in _ns:
        raise NameError(f"Function '{_func_name}' was not found in the code.")

    _fn = _ns[_func_name]
    _sig_params = list(inspect.signature(_fn).parameters.keys())
    _param_names = set(_sig_params)
    _first_param = _sig_params[0] if _sig_params else 'arr'
    _exhausted_loop_vars = set()

    _frame_uid_map = {}
    _next_frame_uid = 0

    def _get_frame_uid(f):
        global _next_frame_uid
        if f not in _frame_uid_map:
            _next_frame_uid += 1
            _frame_uid_map[f] = _next_frame_uid
        return _frame_uid_map[f]

    _visual_ds = create_visual_ds(_payload)

    _raw_kwargs = json.loads(_raw_kwargs_json)
    _eval_args = []
    _eval_kwargs = {}

    for _k, _v_str in _raw_kwargs.items():
        if _k == '*args':
            try:
                _parsed_star = ast.literal_eval(_v_str)
                if isinstance(_parsed_star, (list, tuple)):
                    _eval_args.extend(_parsed_star)
                else:
                    _eval_args.append(_parsed_star)
            except (ValueError, SyntaxError):
                for _tok in [t.strip() for t in _v_str.split(',') if t.strip()]:
                    _eval_args.append(_parse_arg_value(_tok))
        elif _k == '**kwargs':
            try:
                _parsed_kw = ast.literal_eval(_v_str)
                if isinstance(_parsed_kw, dict):
                    for _dk, _dv in _parsed_kw.items():
                        _eval_kwargs[str(_dk)] = _dv
            except (ValueError, SyntaxError):
                for _pair in [p.strip() for p in _v_str.split(',') if '=' in p]:
                    _pk, _pv = _pair.split('=', 1)
                    _eval_kwargs[_pk.strip()] = _parse_arg_value(_pv.strip())
        else:
            _eval_kwargs[_k] = _parse_arg_value(_v_str)

    def _build_state_vars(frame, executed_lineno):
        # Strictly inspect the target algorithm frame so other helper functions'
        # parameters (even if also named `arr`) do not override or pollute the visual DS
        loc = dict(frame.f_locals)
        is_entry_frame = (frame.f_code.co_name == _func_name)

        loop_var_names = _loop_targets.get(executed_lineno, [])
        if is_entry_frame:
            if loop_var_names:
                if getattr(_visual_ds, '_loop_exhausted_on_step', False):
                    _exhausted_loop_vars.update(loop_var_names)
                else:
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

            assigned_names = _assign_targets.get(executed_lineno, [])
            if assigned_names and not getattr(_visual_ds, '_loop_exhausted_on_step', False) and '_NodeId' in globals():
                assigned_node_ids = []
                for name in assigned_names:
                    if name in _param_names:
                        continue
                    val = loc.get(name)
                    if isinstance(val, _NodeId) and str(val) in _visual_ds:
                        assigned_node_ids.append(str(val))
                    elif isinstance(val, (list, tuple)):
                        for item in val:
                            if isinstance(item, _NodeId) and str(item) in _visual_ds:
                                assigned_node_ids.append(str(item))
                if assigned_node_ids:
                    _visual_ds.active_edge = None
                    for nid in assigned_node_ids:
                        _visual_ds.record_visit(nid)

        state_vars = {}
        for k, v in loc.items():
            if (
                not k.startswith('_')
                and v is not _visual_ds
                and (not is_entry_frame or k != _first_param)
                and k not in _exhausted_loop_vars
                and not inspect.isfunction(v)
                and not inspect.ismodule(v)
            ):
                state_vars[k] = _serialize(v)

        if is_entry_frame and hasattr(_visual_ds, 'enhance_state_vars'):
            _visual_ds.enhance_state_vars(state_vars, loc, _first_param)

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
            _get_frame_uid(frame)
            caller = frame.f_back
            if caller is not None and caller.f_code.co_filename == '<algorithm>':
                caller_fid = _get_frame_uid(caller)
                caller_pending = _pending_steps.pop(caller_fid, None)
                if caller_pending is not None:
                    caller_state = _build_state_vars(caller, caller_pending['line'])
                    _trace_steps.append({
                        'event': 'line',
                        'line': caller_pending['line'],
                        'stateVars': caller_state,
                        'visual': _visual_ds.snapshot(),
                    })
                if '_NodeId' in globals():
                    for k, v in frame.f_locals.items():
                        if v is not _visual_ds and isinstance(v, _NodeId) and str(v) in _visual_ds:
                            _visual_ds.active_edge = None
                            _visual_ds.record_visit(str(v))
                _visual_ds.on_step_start()
            return _tracer

        fid = _get_frame_uid(frame)
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
            _frame_uid_map.pop(frame, None)
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
            else:
                caller = frame.f_back
                if caller is not None and caller.f_code.co_filename == '<algorithm>' and '_NodeId' in globals():
                    _visual_ds.active_edge = None
                    for k, v in caller.f_locals.items():
                        if v is not _visual_ds and k not in _loop_targets.get(caller.f_lineno, []) and isinstance(v, _NodeId) and str(v) in _visual_ds:
                            _visual_ds.record_visit(str(v))
                            break

        return _tracer

    _old_rec_limit = sys.getrecursionlimit()
    sys.setrecursionlimit(250)

    sys.settrace(_tracer)
    try:
        _fn(_visual_ds, *_eval_args, **_eval_kwargs)
    finally:
        sys.settrace(None)
        sys.setrecursionlimit(_old_rec_limit)

    _visual_ds.finalize_steps(_trace_steps)

except _WaitForUserChoice as pause_exc:
    _, _, _tb = sys.exc_info()
    _pause_frame = None
    _curr_tb = _tb
    while _curr_tb is not None:
        if _curr_tb.tb_frame.f_code.co_filename == '<algorithm>':
            _pause_frame = _curr_tb.tb_frame
        _curr_tb = _curr_tb.tb_next

    if _pause_frame is not None:
        _pfid = _get_frame_uid(_pause_frame)
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