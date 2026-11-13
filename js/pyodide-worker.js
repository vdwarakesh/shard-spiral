// js/pyodide-worker.js

importScripts('https://cdn.jsdelivr.net/pyodide/v0.26.4/full/pyodide.js');

let pyodideReadyPromise = loadPyodide();
let jediLoadedPromise = null;

function ensureJediLoaded(py) {
    if (!jediLoadedPromise) {
        jediLoadedPromise = py.loadPackage('jedi').then(() =>
            py.runPythonAsync(`import jedi`)
        );
    }
    return jediLoadedPromise;
}

let tracerScriptPromise = fetch('../python/pyodide-worker.py', { cache: 'no-store' }).then(res => {
    if (!res.ok) {
        throw new Error(`Failed to load pyodide-worker.py (Status: ${res.status})`);
    }
    return res.text();
});

const dsProxyScriptCache = new Map();

const toSnakeCase = (str) =>
    String(str || 'array')
        .trim()
        .replace(/['’]/g, '')
        .replace(/\+/g, 'plus')
        .replace(/[^a-zA-Z0-9]+/g, '_')
        .replace(/^_+|_+$/g, '')
        .toLowerCase();

function getDsProxyScript(category) {
    const safeCat = toSnakeCase(category);
    if (!dsProxyScriptCache.has(safeCat)) {
        const promise = fetch(`../python/${safeCat}.py`, { cache: 'no-store' }).then(res => {
            if (!res.ok) {
                throw new Error(`Failed to load ../python/${safeCat}.py (Status: ${res.status})`);
            }
            return res.text();
        });
        dsProxyScriptCache.set(safeCat, promise);
    }
    return dsProxyScriptCache.get(safeCat);
}

self.onmessage = async (event) => {
    const {
        id,
        type,
        dsCategory,
        pythonCode,
        funcName,
        dsData,
        nodeLabels,
        rawKwargs,
        simMode,
        userChoices,
        userInputs,
        maxSteps,
        line,
        column,
    } = event.data;

    if (type === 'warmup') {
        try {
            const py = await pyodideReadyPromise;
            await ensureJediLoaded(py);
            await py.runPythonAsync(`
import sys
import json
import inspect
import traceback
import ast
import math
import heapq
from collections import deque, OrderedDict
            `);
            self.postMessage({ id, status: 'ready' });
        } catch (err) {
            console.error('Worker warm-up failed:', err);
        }
        return;
    }

    if (type === 'complete') {
        try {
            const py = await pyodideReadyPromise;
            await ensureJediLoaded(py);

            let proxyHeader = '';
            if (dsCategory) {
                try {
                    proxyHeader = (await getDsProxyScript(dsCategory)) + '\n';
                } catch (_) {}
            }

            const headerLineOffset = proxyHeader ? proxyHeader.split('\n').length - 1 : 0;
            const fullSource = proxyHeader + (pythonCode || '');

            py.globals.set('_jedi_source', fullSource);
            py.globals.set('_jedi_line', (line || 1) + headerLineOffset);
            py.globals.set('_jedi_col', column || 0);

            const rawCompletions = await py.runPythonAsync(`
import json
import jedi

def _get_jedi_completions(source, line, col):
    try:
        script = jedi.Script(code=source)
        completions = script.complete(line=line, column=col)
        results = []
        for c in completions[:60]:
            # Skip private/dunder attributes unless user explicitly typed '_'
            if c.name.startswith('_') and not c.get_completion_prefix_length():
                continue
            results.append({
                "name": c.name,
                "type": c.type,
                "prefixLen": c.get_completion_prefix_length()
            })
        return json.dumps(results)
    except Exception:
        return "[]"

_get_jedi_completions(_jedi_source, _jedi_line, _jedi_col)
            `);

            self.postMessage({ id, result: JSON.parse(rawCompletions) });
        } catch (err) {
            self.postMessage({ id, result: [] });
        }
        return;
    }

    // Keep your existing "if (type === 'run')" block intact below...
};