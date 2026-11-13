import { getContainerGraphData } from '../../data-structures/graph/graph.js';
import { tracePythonAlgorithm } from '../../../js/pyodide-runner.js';

export async function dijkstras_algorithm(containerEl, rawKwargs = {}, simOptions = {}) {
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
    const w = e.weight !== undefined && e.weight !== null && !Number.isNaN(Number(e.weight))
      ? Number(e.weight)
      : 1;

    if (adjList[u] && !adjList[u].some((pair) => String(pair[0]) === v)) {
      adjList[u].push([v, w]);
    }
    if (!isDirected && u !== v && adjList[v] && !adjList[v].some((pair) => String(pair[0]) === u)) {
      adjList[v].push([u, w]);
    }
  });

  let pythonCode = simOptions.pythonCode;
  if (!pythonCode) {
    const res = await fetch('algorithms/dijkstras_algorithm.py');
    pythonCode = await res.text();
  }

  // Detect top-level entry-point function name (ignoring indented class methods like __init__)
  const fnMatch = pythonCode.match(/^def\s+(?!__\w+__)([a-zA-Z_]\w*)\s*\(/m);
  const funcName = fnMatch ? fnMatch[1] : 'dijkstras_algorithm';

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

  const formatDistMap = (distObj) => {
    if (!distObj || typeof distObj !== 'object') return '{}';
    return `{${Object.entries(distObj)
      .map(([k, v]) => `${k}: ${v}`)
      .join(', ')}}`;
  };

  pyFrames.forEach((frame, idx) => {
    const pyLine = frame.line;
    const sv = frame.stateVars || {};
    const vis = frame.visual;

    // Format dict/tuple state variables cleanly for the State Variables UI
    const displaySv = { ...sv };
    if (displaySv.distances && typeof displaySv.distances === 'object') {
      displaySv.distances = formatDistMap(displaySv.distances);
    }
    if (Array.isArray(displaySv.pq)) {
      displaySv.pq = `[${displaySv.pq
        .map((item) => (Array.isArray(item) ? `(${item.join(', ')})` : String(item)))
        .join(', ')}]`;
    }
    if (displaySv.return && typeof displaySv.return === 'object') {
      displaySv.return = formatDistMap(displaySv.return);
    }

    let stepDescription = `Line ${pyLine}`;
    if (frame.event === 'return') {
      stepDescription = `Dijkstra's complete! Shortest distances: ${displaySv.return}.`;
    } else if (pyLine === 4) {
      stepDescription = `Checking if graph is empty`;
    } else if (pyLine === 6) {
      stepDescription = `Checking if start_node was provided`;
    } else if (pyLine === 7) {
      stepDescription = `Defaulting start_node to first node in graph`;
    } else if (pyLine === 8) {
      stepDescription = `Verifying start_node exists in graph`;
    } else if (pyLine === 10) {
      stepDescription = `Initializing all node distances to ∞`;
    } else if (pyLine === 11) {
      stepDescription = `Setting distance to start_node '${sv.start_node}' as 0`;
    } else if (pyLine === 12) {
      stepDescription = `Initializing min-priority queue with (0, '${sv.start_node}')`;
    } else if (pyLine === 13) {
      stepDescription = `Initializing empty visited list`;
    } else if (pyLine === 14) {
      stepDescription = `Checking if priority queue has entries remaining`;
    } else if (pyLine === 15) {
      stepDescription = `Popped node '${sv.node}' with current shortest distance ${sv.curr_dist}`;
    } else if (pyLine === 16) {
      stepDescription = `Checking if node '${sv.node}' has already been finalized`;
    } else if (pyLine === 17) {
      stepDescription = `Skipping '${sv.node}' because it was already finalized`;
    } else if (pyLine === 18) {
      stepDescription = `Marking node '${sv.node}' as finalized (visited)`;
    } else if (pyLine === 19) {
      stepDescription =
        vis.activeEdge && sv.neighbor !== undefined
          ? `Inspecting edge '${sv.node}' → '${sv.neighbor}' (weight: ${sv.weight})`
          : `Finished relaxing all outgoing edges of '${sv.node}'`;
    } else if (pyLine === 20) {
      stepDescription = `Calculating candidate distance to '${sv.neighbor}': ${sv.curr_dist} + ${sv.weight} = ${sv.new_dist}`;
    } else if (pyLine === 21) {
      const oldDist = sv.distances ? sv.distances[sv.neighbor] : '∞';
      stepDescription = `Comparing new distance (${sv.new_dist}) with current best distance to '${sv.neighbor}' (${oldDist})`;
    } else if (pyLine === 22) {
      stepDescription = `Updating shortest distance to '${sv.neighbor}' = ${sv.new_dist}`;
    } else if (pyLine === 23) {
      stepDescription = `Pushing (${sv.new_dist}, '${sv.neighbor}') into priority queue`;
    } else if (pyLine === 24) {
      stepDescription = `Priority queue is empty. Returning shortest distances.`;
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
      stateVars: displaySv,
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

// Export aliases so it works whether named "Dijkstra's", "Dijkstra's Algorithm", or "Dijkstra's Shortest Path"
export {
  dijkstras_algorithm as dijkstras,
  dijkstras_algorithm as dijkstra,
  dijkstras_algorithm as dijkstras_shortest_path,
  dijkstras_algorithm as default,
};