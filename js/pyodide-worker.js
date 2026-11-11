// js/pyodide-worker.js

importScripts('https://cdn.jsdelivr.net/pyodide/v0.26.4/full/pyodide.js');

let pyodideReadyPromise = loadPyodide();

let tracerScriptPromise = fetch('../python/pyodide-worker.py').then(res => {
    if (!res.ok) {
        throw new Error(`Failed to load pyodide-worker.py (Status: ${res.status})`);
    }
    return res.text();
});

// Cache for separate per-data-structure Python proxy files (e.g. sequence.py, graph.py)
const dsProxyScriptCache = new Map();

function getDsProxyScript(category) {
    const safeCat = (category || 'sequence').toLowerCase().trim();
    if (!dsProxyScriptCache.has(safeCat)) {
        const promise = fetch(`../python/${safeCat}.py`).then(res => {
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
        maxSteps,
    } = event.data;

    if (type === 'warmup') {
        try {
            const py = await pyodideReadyPromise;
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

    if (type === 'run') {
        try {
            const category = dsCategory || 'sequence';
            const [py, tracerScript, dsProxyCode] = await Promise.all([
                pyodideReadyPromise,
                tracerScriptPromise,
                getDsProxyScript(category),
            ]);

            py.globals.set('_user_code', pythonCode);
            py.globals.set('_func_name', funcName);
            py.globals.set('_ds_category', category);
            py.globals.set('_ds_proxy_code', dsProxyCode);
            py.globals.set('_ds_payload_json', JSON.stringify(dsData ?? []));
            py.globals.set('_node_labels_json', JSON.stringify(nodeLabels || {}));
            py.globals.set('_raw_kwargs_json', JSON.stringify(rawKwargs || {}));
            py.globals.set('_sim_mode', simMode || 'auto');
            py.globals.set('_user_choices_json', JSON.stringify(userChoices || []));
            py.globals.set('_MAX_STEPS', maxSteps || 2500);

            const rawJson = await py.runPythonAsync(tracerScript);

            self.postMessage({ id, result: JSON.parse(rawJson) });
        } catch (fatalErr) {
            self.postMessage({
                id,
                result: {
                    steps: [],
                    error: {
                        type: 'RuntimeError',
                        message: fatalErr.message || String(fatalErr),
                        line: null,
                    },
                },
            });
        }
    }
};