import { getContainerGraphData } from '../../data-structures/graph/graph.js';
import { tracePythonAlgorithm } from '../../../js/pyodide-runner.js';

export async function breadth_first_search_bfs(containerEl, rawKwargs = {}, simOptions = {}) {
  const graphData = getContainerGraphData(containerEl);
  const { nodes, edges, isDirected } = graphData;

  const adjList = {};
  const nodeLabels = {};

  nodes.forEach((n) => {
    const idStr = String(n.id);
    adjList[idStr] = [];
    nodeLabels[idStr] = String(n.label !== undefined ? n.label : n.id);
  });

  edges.forEach((e) => {
    const u = String(typeof e.source === 'object' ? e.source.id : e.source);
    const v = String(typeof e.target === 'object' ? e.target.id : e.target);
    if (adjList[u] && !adjList[u].includes(v)) {
      adjList[u].push(v);
    }
    if (!isDirected && u !== v && adjList[v] && !adjList[v].includes(u)) {
      adjList[v].push(u);
    }
  });

  
  if (!pythonCode) {
    const pyUrl = new URL('../../../dsa/Graph/Algorithms/breadth_first_search_bfs.py', import.meta.url);
    const res = await fetch(pyUrl);
    if (!res.ok) {
      throw new Error(`Failed to load Python file (${res.status})`);
    }
    pythonCode = await res.text();
  }

  // Detect the entry-point function name from the user's code (fallback to 'breadth_first_search')
  const fnMatch = pythonCode.match(/^def\s+(?!__\w+__)([a-zA-Z_]\w*)\s*\(/m);
  const funcName = fnMatch ? fnMatch[1] : 'breadth_first_search';

  const { steps: pyFrames, error } = await tracePythonAlgorithm({
    dsCategory: 'graph',
    pythonCode,
    funcName,
    dsData: adjList,
    nodeLabels,
    rawKwargs,
    simMode: simOptions.mode || 'auto',
    userChoices: simOptions.userChoices || [],
  });

  const steps = [];
  const fullExplanationLines = [];

  pyFrames.forEach((frame, idx) => {
    const pyLine = frame.line;
    const sv = frame.stateVars || {};
    const vis = frame.visual;

    let stepDescription = `Line ${pyLine}`;
    if (frame.event === 'return') {
      stepDescription = `BFS complete! Traversal order: [${(sv.return || []).join(', ')}].`;
    } else if (pyLine === 2) {
      stepDescription = `Checking if graph is empty`;
    } else if (pyLine === 4) {
      stepDescription = `Checking if start_node was provided`;
    } else if (pyLine === 5) {
      stepDescription = `Defaulting start_node to first node in graph`;
    } else if (pyLine === 8) {
      stepDescription = `Marking start_node as visited`;
    } else if (pyLine === 9) {
      stepDescription = `Initializing queue with start_node: [${(sv.queue || []).join(', ')}]`;
    } else if (pyLine === 10) {
      stepDescription = `Initializing empty traversal order list`;
    } else if (pyLine === 11) {
      stepDescription = `Checking if queue has nodes remaining (queue: [${(sv.queue || []).join(', ')}])`;
    } else if (pyLine === 12) {
      stepDescription = `Dequeued node '${sv.node}' from front of queue`;
    } else if (pyLine === 13) {
      stepDescription = `Visiting node '${sv.node}' - order is now [${(sv.order || []).join(', ')}]`;
    } else if (pyLine === 14) {
      stepDescription =
        vis.activeEdge && sv.neighbor !== undefined
          ? `Inspecting edge from '${sv.node}' to neighbor '${sv.neighbor}'`
          : `Finished checking all neighbors of '${sv.node}'`;
    } else if (pyLine === 15) {
      stepDescription = `Checking if neighbor '${sv.neighbor}' has already been visited`;
    } else if (pyLine === 16) {
      stepDescription = `Marking neighbor '${sv.neighbor}' as visited`;
    } else if (pyLine === 17) {
      stepDescription = `Enqueuing neighbor '${sv.neighbor}' into queue: [${(sv.queue || []).join(', ')}]`;
    } else if (pyLine === 18) {
      stepDescription = `Queue is empty. Returning BFS traversal order.`;
    }

    if (frame.interaction) {
      stepDescription = frame.interaction.title;
    }

    fullExplanationLines.push(`Step ${idx + 1}: ${stepDescription}`);

    steps.push({
      lines: {
        Python: { active: String(pyLine) },
      },
      activeLineKey: 'active',
      activeIndex: -1,
      foundIndex: -1,
      checkedIndices: [],
      activeNodeId: vis.activeNodeId,
      activeNodeIds: vis.activeNodeIds || [],
      foundNodeId: null,
      visitedNodes: vis.visitedNodes,
      activeEdge: vis.activeEdge,
      visitedEdges: vis.visitedEdges,
      traversal: vis.traversal,
      stateVars: sv,
      stepDescription,
      interaction: frame.interaction || null,
    });
  });

  if (error) {
    const errLine = error.line || (pyFrames.length ? pyFrames[pyFrames.length - 1].line : 1);
    const lastStep = steps[steps.length - 1];
    const errDesc = `${error.type}: ${error.message}`;

    fullExplanationLines.push(`Error (Line ${errLine}): ${errDesc}`);

    steps.push({
      lines: {
        Python: { active: String(errLine) },
      },
      activeLineKey: 'active',
      activeIndex: -1,
      foundIndex: -1,
      checkedIndices: [],
      activeNodeId: lastStep ? lastStep.activeNodeId : null,
      activeNodeIds: lastStep ? lastStep.activeNodeIds || [] : [],
      foundNodeId: null,
      visitedNodes: lastStep ? lastStep.visitedNodes : [],
      activeEdge: lastStep ? lastStep.activeEdge : null,
      visitedEdges: lastStep ? lastStep.visitedEdges : [],
      stateVars: {
        ...(lastStep ? lastStep.stateVars : {}),
        error: errDesc,
      },
      stepDescription: errDesc,
      isError: true,
    });
  }

  return { steps, fullExplanationLines, error };
}