// js/pyodide-runner.js

// Spawn the background worker immediately when this file is imported
const worker = new Worker('js/pyodide-worker.js');

let messageIdCounter = 0;
const pendingResolves = new Map();

// Listen for results coming back from the background thread
worker.onmessage = (event) => {
  const { id, result } = event.data;
  if (pendingResolves.has(id)) {
    pendingResolves.get(id)(result);
    pendingResolves.delete(id);
  }
};

export function warmUpPyodide() {
  worker.postMessage({ id: -1, type: 'warmup' });
}

/**
 * Unified generic Python algorithm tracer.
 * @param {Object} config
 * @param {'sequence'|'graph'} config.dsCategory - Proxy category to wrap the input data structure in
 * @param {string} config.pythonCode - Raw Python source code
 * @param {string} config.funcName - Entry function name in Python
 * @param {*} config.dsData - Serialized data structure payload (e.g. array of values, or adjacency dict)
 * @param {Object} [config.nodeLabels={}] - Optional ID -> display label map (for graphs/trees)
 * @param {Object} [config.rawKwargs={}] - User-supplied keyword arguments from the UI
 * @param {number} [config.maxSteps=2500] - Maximum execution steps before InfiniteLoopError
 */
export function tracePythonAlgorithm({
  dsCategory = 'array',
  pythonCode,
  funcName,
  dsData,
  nodeLabels = {},
  rawKwargs = {},
  simMode = 'auto',
  userChoices = [],
  userInputs = [],
  maxSteps = 2500,
}) {
  return new Promise((resolve) => {
    const id = messageIdCounter++;
    pendingResolves.set(id, resolve);

    worker.postMessage({
      id,
      type: 'run',
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
    });
  });
}