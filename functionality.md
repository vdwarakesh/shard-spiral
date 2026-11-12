# Python Tracer Architecture & Functionality

This document details the internal execution environment of the Python algorithm tracer. The system relies on a combination of Abstract Syntax Tree (AST) parsing, `sys.settrace` for step-by-step state extraction, deterministic replay for interactivity, and the Proxy pattern for data structures.

## 1. Algorithm Resolution & Execution Namespace

When the user provides a custom algorithm string, it is not run directly in the global environment. It is sandboxed and parsed to ensure safe and predictable tracing.

* **Namespace Isolation (`_ns`):** The user's code is executed via `exec(compile(code, '<algorithm>', 'exec'), _ns)`. The `_ns` dictionary serves as an isolated namespace.
* **Builtin Overrides:** Before execution, standard I/O functions are overridden. A custom `print` appends to a `_stdout_buffer`, and a custom `input` hooks into the interactivity engine (detailed below). These are injected into `_ns['__builtins__']`.
* **Function Discovery:** The engine uses Python's `ast` (Abstract Syntax Tree) module to walk through the user's code. It identifies all `ast.FunctionDef` nodes to locate the top-level algorithm function (e.g., `my_array_algorithm`).
* **Invocation:** Once the function is located in `_ns` (e.g., `_fn = _ns[_func_name]`), it is invoked dynamically. The engine passes the active Data Structure Proxy as the first argument, followed by any standard parameters extracted from the user's configuration.

## 2. Data Structure Proxies (The `Visual*` Classes)

The engine never passes standard Python `list` or `dict` objects to the user's algorithm. Instead, it passes tightly controlled subclasses-like `VisualArray` or `VisualGraph`-that act as spies.

* **Subclassing Standard Types:** `VisualArray` inherits directly from `list`, and `VisualGraph` inherits from `dict`. This means they support all standard Python operations natively (`len(arr)`, `graph[u]`, `arr.append(x)`).
* **Operation Interception:** Magic methods (dunder methods) are overridden to record operations. For example, in `VisualArray`:
* When `arr[i]` is accessed, `__getitem__(self, idx)` intercepts the call.
* It updates internal state variables like `self.active_index = idx`.
* It then calls `super().__getitem__(idx)` to return the actual value.


* **State Snapshots:** Every proxy class implements a `snapshot()` method. During execution, the tracer calls this method to retrieve a dictionary representing the structure's exact state at that specific line of code (e.g., which index is currently being accessed, which indices have already been checked).

## 3. The Line-by-Line Tracer (`sys.settrace`)

The engine uses `sys.settrace(_tracer)` to hook into the Python interpreter at runtime. The `_tracer` function is called automatically by Python on three specific events:

1. **`call`:** Triggered when a new function frame is pushed onto the stack. The tracer assigns a unique ID to the frame. If a recursive helper function is called (e.g., `_dfs(neighbor)`), the tracer ensures the proxy object's active state highlights the new argument.
2. **`line`:** Triggered right before a line of code executes. The tracer captures the local variables (`frame.f_locals`), filters out internal or unneeded variables, formats them into `stateVars`, and calls `_visual_ds.snapshot()`.
3. **`return`:** Triggered when a function returns a value. The tracer intercepts the return value, adds it to `stateVars['return']`, and commands the proxy to handle a "found" state if applicable.

*Note: The AST is also used here to map `while` loops and variable assignments. The proxy's `on_line_fallback()` method uses this AST data to ensure variables assigned on a specific line (e.g., `cur = queue.pop(0)`) are accurately highlighted as the "active" nodes/indices.*

## 4. Interactivity & Exception Handling (Pause / Resume)

Python's `sys.settrace` cannot asynchronously yield execution. Therefore, interactive prompts (like `input()` or manual graph neighbor selection) rely on a **Deterministic Replay Architecture** utilizing the `_WaitForUserChoice` exception.

### How Pausing Works:

1. When the algorithm hits `input("Prompt: ")`, the overridden `_custom_input` function checks a pre-populated list of answers (`_user_inputs`).
2. If the list is empty (meaning the user hasn't answered yet), the engine immediately stops tracing (`sys.settrace(None)`).
3. It raises a custom exception: `raise _WaitForUserChoice({'type': 'stdin_input', 'prompt': ...})`.
4. The main wrapper catches this exception. It records the final, paused frame state, attaches the interaction request metadata, and exits completely.

### How Resuming Works:

1. When the user submits their answer, the environment is restarted from scratch.
2. The answer is pushed into the `_user_inputs` (or `_user_choices`) list, which is injected into the Python environment globals.
3. The algorithm runs from the beginning at maximum speed. Because the environment is deterministic, it traces the exact same path.
4. When it reaches the `input()` call again, `_custom_input` sees that `_user_inputs` is no longer empty. It pops the answer, returns it to the user's script, and the algorithm continues stepping forward to new lines of code.

## 5. Extending Proxies (Adding Functionality to `array.py`)

The proxy architecture is designed to be easily extensible. If you want to add custom helper methods to a data structure (e.g., a `swap` method for sorting algorithms), you modify its proxy class.

**Example: Adding a `swap` method to `VisualArray**`
To allow users to write `arr.swap(i, j)` and have it visually tracked, you would add the following method to `VisualArray` in `array.py`:

```python
    def swap(self, i, j):
        """Swaps two elements in the array and records the interaction for the snapshot."""
        # 1. Normalize negative indices
        n = len(self)
        norm_i = i if i >= 0 else n + i
        norm_j = j if j >= 0 else n + j
        
        # 2. Record the access for the visualizer
        self._record_access(norm_i)
        self._record_access(norm_j)
        
        # 3. Mark them as checked since they are being manipulated
        if norm_i not in self.checked_indices:
            self.checked_indices.append(norm_i)
        if norm_j not in self.checked_indices:
            self.checked_indices.append(norm_j)
            
        # 4. Perform the actual underlying swap
        temp = super().__getitem__(norm_i)
        super().__setitem__(norm_i, super().__getitem__(norm_j))
        super().__setitem__(norm_j, temp)

```

**How to extend standard behavior:**

* **New Dunder Methods:** You can intercept math operations by adding `__add__` or `__iadd__`.
* **Custom Node/Edge states:** If building a Tree structure, you can subclass `VisualTree` and add a `mark_branch_pruned(node)` method, which updates an internal `self.pruned_nodes` list. The `snapshot()` method would then be updated to return `'prunedNodes': list(self.pruned_nodes)`.