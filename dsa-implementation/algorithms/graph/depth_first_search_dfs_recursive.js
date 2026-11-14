import { getContainerGraphData } from '../../data-structures/graph/graph.js';
import { tracePythonAlgorithm } from '../../../js/pyodide-runner.js';

export async function depth_first_search_dfs(containerEl, rawKwargs = {}, simOptions = {}) {
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

  let pythonCode = simOptions.pythonCode;
  if (!pythonCode) {
    const pyUrl = new URL('../../../dsa/Graph/Algorithms/depth_first_search_dfs_recursive.py', import.meta.url);
    const res = await fetch(pyUrl);
    if (!res.ok) {
      throw new Error(`Failed to load Python file (${res.status})`);
    }
    pythonCode = await res.text();
  }

  // Detect top-level entry-point function name (ignoring indented class methods like __init__)
  const fnMatch = pythonCode.match(/^def\s+(?!__\w+__)([a-zA-Z_]\w*)\s*\(/m);
  const funcName = fnMatch ? fnMatch[1] : 'depth_first_search';

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
      stepDescription = `DFS complete! Traversal order: [${(sv.return || []).join(', ')}].`;
    } else if (pyLine === 2) {
      stepDescription = `Checking if graph is empty`;
    } else if (pyLine === 4) {
      stepDescription = `Checking if start_node was provided`;
    } else if (pyLine === 5) {
      stepDescription = `Defaulting start_node to first node in graph`;
    } else if (pyLine === 6) {
      stepDescription = `Verifying start_node exists in graph`;
    } else if (pyLine === 9) {
      stepDescription = `Initializing empty visited list`;
    } else if (pyLine === 10) {
      stepDescription = `Initializing empty traversal order list`;
    } else if (pyLine === 12) {
      stepDescription = `Defining recursive helper function '_dfs(node)'`;
    } else if (pyLine === 13) {
      stepDescription = `Marking node '${sv.node}' as visited`;
    } else if (pyLine === 14) {
      stepDescription = `Appending node '${sv.node}' to traversal order`;
    } else if (pyLine === 15) {
      stepDescription =
        vis.activeEdge && sv.neighbor !== undefined
          ? `Inspecting edge from '${sv.node}' to neighbor '${sv.neighbor}'`
          : `Finished checking all neighbors of '${sv.node}', backtracking to caller...`;
    } else if (pyLine === 16) {
      stepDescription = `Checking if neighbor '${sv.neighbor}' has already been visited`;
    } else if (pyLine === 17) {
      stepDescription = `Neighbor '${sv.neighbor}' is unvisited. Making recursive call _dfs('${sv.neighbor}')`;
    } else if (pyLine === 19) {
      stepDescription = `Starting initial recursive DFS call from start_node: '${sv.start_node}'`;
    } else if (pyLine === 20) {
      stepDescription = `Initial call returned. Returning final DFS traversal order.`;
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

// Export aliases so it works whether named "DFS", "Depth First Search", or "Depth First Search (DFS)"
export {
  depth_first_search_dfs as dfs,
  depth_first_search_dfs as depth_first_search,
  depth_first_search_dfs as default,
};