// data-structures/Graph.js

import * as d3Module from './d3.js'; // Adjust path to your d3.js as needed
const d3 = window.d3 || d3Module;

const textMeasurementContext = document.createElement('canvas').getContext('2d');

// ========== Hyperparameters ==========
export const GRAPH_HYPERPARAMETERS = {
  // ----- Node Dimensions & Geometry -----
  NODE_MIN_WIDTH: 60,           // Minimum width of a node in world px
  NODE_HEIGHT: 60,              // Fixed height of a node in world px
  NODE_PADDING_X: 20,           // Horizontal inner padding on each side of the node label
  NODE_CORNER_RADIUS: 30,       // Corner radius (30px with 60px height creates a pill/circle)
  NODE_STROKE_WIDTH: 0,       // Border thickness of nodes

  // ----- Edge Geometry & Hit Testing -----
  EDGE_STROKE_WIDTH: 4,         // Visible thickness of graph edges
  EDGE_HIT_BUFFER_WIDTH: 20,    // Transparent stroke width used for mouse hover/click hit-testing
  BIDIRECTIONAL_OFFSET: -8,     // Perpendicular pixel offset for curved bidirectional edge pairs
  BIDIRECTIONAL_ARC_FACTOR: 1.2,// Multiplier on node distance to compute arc radius
  SELF_LOOP_RADIUS: 50,         // Radius of the circular self-loop path
  SELF_LOOP_OFFSET_X: 0,        // Horizontal offset of self-loop anchor from node center
  SELF_LOOP_OFFSET_Y: -35,      // Vertical offset of self-loop anchor from node center
  SELF_LOOP_LABEL_OFFSET_X: -5, // Horizontal offset for weight label on a self-loop
  SELF_LOOP_LABEL_OFFSET_Y: -85,// Vertical offset for weight label on a self-loop

  // ----- Directed Arrowhead Geometry -----
  ARROW_SCALE: 2,               // Scale multiplier for the (-5..5, 0..10) arrowhead polygon
  ARROW_REF_X: 9,               // Standard arrowhead tip pullback along edge tangent
  ARROW_REF_Y: 0,               // Standard arrowhead perpendicular offset
  ARROW_SELF_LOOP_REF_X: 4,     // Self-loop arrowhead tip pullback
  ARROW_SELF_LOOP_REF_Y: -0.5,  // Self-loop arrowhead perpendicular offset

  // ----- Circular Layout & Crossing Minimization -----
  MIN_NODE_GAP: 200,            // Minimum arc gap between nodes around the layout circle
  MIN_CIRCLE_RADIUS: 150,       // Floor on the circular layout radius in world px
  CROSSING_MAX_ITERATIONS: 20000,// Simulated annealing iterations for minimizing edge crossings
  INITIAL_TEMPERATURE: 2.0,     // Starting temperature for simulated annealing
  FINAL_TEMPERATURE: 0.01,      // Ending temperature floor for simulated annealing
  BOUNDS_PADDING: 25,           // World-space margin added around nodes/edges for zoom-to-fit

  // ----- Fonts & Weight Pill Badges -----
  FONT_FAMILY: "'Adwaita Sans', -apple-system, BlinkMacSystemFont, sans-serif",
  NODE_FONT_SIZE: 25,
  NODE_FONT_WEIGHT: 'bold',
  EDGE_LABEL_FONT_SIZE: 25,
  EDGE_LABEL_FONT_WEIGHT: 'bold',
  WEIGHT_PILL_PADDING_X: 15,     // Horizontal padding inside the edge weight badge
  WEIGHT_PILL_HEIGHT: 40,       // Height of the edge weight badge
  WEIGHT_PILL_RADIUS: 6,        // Corner radius of the edge weight badge
  WEIGHT_PILL_STROKE_WIDTH: 4,// Border width of the edge weight badge

  // ----- Colors: CSS variable names (guaranteed to exist on :root) -----
  NODE_FILL_VAR: '--ds-primary',
  NODE_STROKE_VAR: '--bg-card',
  NODE_DRAG_FILL_VAR: '--ds-hover-primary',

  EDGE_STROKE_VAR: '--ds-secondary',
  EDGE_HOVER_STROKE_VAR: '--ds-hover-secondary',

  TEXT_BRIGHT_VAR: '--text-bright',
  TEXT_DARK_VAR: '--text-dark',
  WEIGHT_BG_VAR: '--bg-card',

  // Simulation state variables
  CURRENT_FILL_VAR: '--ds-current-fill',
  CHECKED_COLOR_VAR: '--ds-checked-primary',
  EDGE_VISITED_VAR: '--ds-checked-secondary',

  CANDIDATE_VAR: '--ds-current-fill',
  SOURCE_NODE_VAR: '--ds-hover-secondary',
  DEFAULT_ALPHA: 1,
};

/**
 * Resolves CSS variables into concrete colors.
 */
function resolveStyleHyperparameters(hp) {
  const rootStyle = getComputedStyle(document.documentElement);
  const resolved = { ...hp };

  const readVar = (varName) => {
    const val = rootStyle.getPropertyValue(varName).trim();
    return val || '#000000'; // Fallback to prevent canvas errors if css var is missing
  };

  resolved.NODE_FILL = readVar(hp.NODE_FILL_VAR);
  resolved.NODE_STROKE = readVar(hp.NODE_STROKE_VAR);
  resolved.NODE_DRAG_FILL = readVar(hp.NODE_DRAG_FILL_VAR);

  resolved.EDGE_STROKE = readVar(hp.EDGE_STROKE_VAR);
  resolved.EDGE_HOVER_STROKE = readVar(hp.EDGE_HOVER_STROKE_VAR);
  resolved.CANDIDATE = readVar(hp.CANDIDATE_VAR);

  resolved.TEXT_BRIGHT = readVar(hp.TEXT_BRIGHT_VAR);
  resolved.TEXT_DARK = readVar(hp.TEXT_DARK_VAR);
  resolved.WEIGHT_BG = readVar(hp.WEIGHT_BG_VAR);

  resolved.EDGE_VISITED = readVar(hp.EDGE_VISITED_VAR);
  resolved.CURRENT_FILL = readVar(hp.CURRENT_FILL_VAR);
  resolved.CHECKED_COLOR = readVar(hp.CHECKED_COLOR_VAR);
  resolved.SOURCE_NODE = rootStyle.getPropertyValue(hp.SOURCE_NODE_VAR).trim() || resolved.CHECKED_COLOR;

  return resolved;
}

// ============================================================================
// 1. NODE SIZING & POSITIONING
// ============================================================================

function getNodeFont(hp = GRAPH_HYPERPARAMETERS) {
  return `${hp.NODE_FONT_WEIGHT} ${hp.NODE_FONT_SIZE}px ${hp.FONT_FAMILY}`;
}

function getEdgeLabelFont(hp = GRAPH_HYPERPARAMETERS) {
  return `${hp.EDGE_LABEL_FONT_WEIGHT} ${hp.EDGE_LABEL_FONT_SIZE}px ${hp.FONT_FAMILY}`;
}

function measureNodeLabelWidth(text, hp = GRAPH_HYPERPARAMETERS) {
  textMeasurementContext.font = getNodeFont(hp);
  return textMeasurementContext.measureText(String(text)).width;
}

function calculateNodeWidth(nodeData, hp = GRAPH_HYPERPARAMETERS) {
  const displayText = nodeData.label !== undefined ? nodeData.label : nodeData.id;
  return Math.max(hp.NODE_MIN_WIDTH, measureNodeLabelWidth(displayText, hp) + hp.NODE_PADDING_X * 2);
}

// ============================================================================
// 2. EDGE GEOMETRY & ALIGNMENT
// ============================================================================

function calculateRectBorderIntersection(centerX, centerY, halfWidth, halfHeight, targetX, targetY, cornerRadius) {
  const deltaX = targetX - centerX;
  const deltaY = targetY - centerY;
  if (deltaX === 0 && deltaY === 0) return { x: centerX, y: centerY };

  const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY);
  const unitX = deltaX / distance;
  const unitY = deltaY / distance;

  const scaleX = deltaX !== 0 ? halfWidth / Math.abs(deltaX) : Infinity;
  const scaleY = deltaY !== 0 ? halfHeight / Math.abs(deltaY) : Infinity;

  const borderScale = Math.min(scaleX, scaleY, 1);
  const flatIntersectionX = deltaX * borderScale;
  const flatIntersectionY = deltaY * borderScale;

  const clampedRadius = Math.min(cornerRadius || 0, halfWidth, halfHeight);
  if (clampedRadius <= 0) {
    return { x: centerX + flatIntersectionX, y: centerY + flatIntersectionY };
  }

  const innerHalfWidth = halfWidth - clampedRadius;
  const innerHalfHeight = halfHeight - clampedRadius;
  const hitVerticalEdge = scaleX <= scaleY;
  const isInCornerZone = hitVerticalEdge
    ? Math.abs(flatIntersectionY) > innerHalfHeight
    : Math.abs(flatIntersectionX) > innerHalfWidth;

  if (!isInCornerZone) {
    return { x: centerX + flatIntersectionX, y: centerY + flatIntersectionY };
  }

  const cornerCenterX = Math.sign(deltaX) * innerHalfWidth;
  const cornerCenterY = Math.sign(deltaY) * innerHalfHeight;
  const dotProduct = unitX * cornerCenterX + unitY * cornerCenterY;
  const distanceSquaredDiff = cornerCenterX * cornerCenterX + cornerCenterY * cornerCenterY - clampedRadius * clampedRadius;
  const rayDistance = Math.min(dotProduct + Math.sqrt(Math.max(dotProduct * dotProduct - distanceSquaredDiff, 0)), distance);

  return { x: centerX + unitX * rayDistance, y: centerY + unitY * rayDistance };
}

function calculateEdgePathAndLabelPosition(edgeData, hp = GRAPH_HYPERPARAMETERS) {
  if (edgeData.selfLoop) {
    const nodeX = edgeData.source.x;
    const nodeY = edgeData.source.y;
    const loopRadius = hp.SELF_LOOP_RADIUS;
    const offsetX = hp.SELF_LOOP_OFFSET_X;
    const offsetY = hp.SELF_LOOP_OFFSET_Y;

    const startX = nodeX + offsetX;
    const startY = nodeY + offsetY - loopRadius;

    return {
      svgPath: `M${startX},${startY} a${loopRadius},${loopRadius} 0 1,1 0,${2 * loopRadius} a${loopRadius},${loopRadius} 0 1,1 0,${-2 * loopRadius}`,
      labelX: nodeX + offsetX + hp.SELF_LOOP_LABEL_OFFSET_X,
      labelY: nodeY + hp.SELF_LOOP_LABEL_OFFSET_Y,
      arrowX: startX,
      arrowY: startY,
      arrowAngle: 0,
      isSelfLoop: true,
      bounds: {
        minX: nodeX + offsetX - loopRadius,
        maxX: nodeX + offsetX + loopRadius,
        minY: nodeY + offsetY - loopRadius,
        maxY: nodeY + offsetY + loopRadius
      }
    };
  }

  if (edgeData.bidirectional) {
    const sourceHalfWidth = calculateNodeWidth(edgeData.source, hp) / 2;
    const sourceHalfHeight = hp.NODE_HEIGHT / 2;
    const targetHalfWidth = calculateNodeWidth(edgeData.target, hp) / 2;
    const targetHalfHeight = hp.NODE_HEIGHT / 2;

    const startPoint = calculateRectBorderIntersection(
      edgeData.source.x, edgeData.source.y, sourceHalfWidth, sourceHalfHeight,
      edgeData.target.x, edgeData.target.y, hp.NODE_CORNER_RADIUS
    );
    const endPoint = calculateRectBorderIntersection(
      edgeData.target.x, edgeData.target.y, targetHalfWidth, targetHalfHeight,
      edgeData.source.x, edgeData.source.y, hp.NODE_CORNER_RADIUS
    );

    const centerDeltaX = edgeData.target.x - edgeData.source.x;
    const centerDeltaY = edgeData.target.y - edgeData.source.y;
    const centerDistance = Math.sqrt(centerDeltaX * centerDeltaX + centerDeltaY * centerDeltaY) || 1;
    const arcRadius = centerDistance * hp.BIDIRECTIONAL_ARC_FACTOR;

    const perpendicularOffsetX = (-centerDeltaY / centerDistance) * hp.BIDIRECTIONAL_OFFSET;
    const perpendicularOffsetY = (centerDeltaX / centerDistance) * hp.BIDIRECTIONAL_OFFSET;
    startPoint.x += perpendicularOffsetX;
    startPoint.y += perpendicularOffsetY;
    endPoint.x += perpendicularOffsetX;
    endPoint.y += perpendicularOffsetY;

    const chordDeltaX = endPoint.x - startPoint.x;
    const chordDeltaY = endPoint.y - startPoint.y;
    const chordLength = Math.sqrt(chordDeltaX * chordDeltaX + chordDeltaY * chordDeltaY) || 1;
    const midPointX = (startPoint.x + endPoint.x) / 2;
    const midPointY = (startPoint.y + endPoint.y) / 2;
    const sagittaHeight = Math.sqrt(Math.max(arcRadius * arcRadius - (chordLength / 2) * (chordLength / 2), 0));

    const normalX = -chordDeltaY / chordLength;
    const normalY = chordDeltaX / chordLength;
    const circleCenterX = midPointX + normalX * sagittaHeight;
    const circleCenterY = midPointY + normalY * sagittaHeight;
    const radialX = endPoint.x - circleCenterX;
    const radialY = endPoint.y - circleCenterY;
    const arrowAngle = Math.atan2(radialX, -radialY);

    const labelX = midPointX + (arcRadius - sagittaHeight) * (chordDeltaY / chordLength);
    const labelY = midPointY - (arcRadius - sagittaHeight) * (chordDeltaX / chordLength);

    return {
      svgPath: `M${startPoint.x},${startPoint.y}A${arcRadius},${arcRadius} 0 0,1 ${endPoint.x},${endPoint.y}`,
      labelX,
      labelY,
      arrowX: endPoint.x,
      arrowY: endPoint.y,
      arrowAngle,
      isSelfLoop: false,
      bounds: {
        minX: Math.min(startPoint.x, endPoint.x, labelX),
        maxX: Math.max(startPoint.x, endPoint.x, labelX),
        minY: Math.min(startPoint.y, endPoint.y, labelY),
        maxY: Math.max(startPoint.y, endPoint.y, labelY)
      }
    };
  }

  const targetHalfWidth = calculateNodeWidth(edgeData.target, hp) / 2;
  const targetHalfHeight = hp.NODE_HEIGHT / 2;
  const endPoint = calculateRectBorderIntersection(
    edgeData.target.x, edgeData.target.y, targetHalfWidth, targetHalfHeight,
    edgeData.source.x, edgeData.source.y, hp.NODE_CORNER_RADIUS
  );

  const arrowAngle = Math.atan2(endPoint.y - edgeData.source.y, endPoint.x - edgeData.source.x);

  return {
    svgPath: `M${edgeData.source.x},${edgeData.source.y}L${endPoint.x},${endPoint.y}`,
    labelX: (edgeData.source.x + endPoint.x) / 2,
    labelY: (edgeData.source.y + endPoint.y) / 2,
    arrowX: endPoint.x,
    arrowY: endPoint.y,
    arrowAngle,
    isSelfLoop: false,
    bounds: {
      minX: Math.min(edgeData.source.x, endPoint.x),
      maxX: Math.max(edgeData.source.x, endPoint.x),
      minY: Math.min(edgeData.source.y, endPoint.y),
      maxY: Math.max(edgeData.source.y, endPoint.y)
    }
  };
}

// ============================================================================
// 3. CIRCULAR LAYOUT & CROSSING MINIMIZATION
// ============================================================================

export function applyCircularNodeLayout(nodes, canvasWidth, canvasHeight, edges = [], hp = GRAPH_HYPERPARAMETERS) {
  if (!nodes || nodes.length === 0) return;

  const getNodeId = node => node.id !== undefined ? node.id : node.label || node.name;
  const getEndpointId = endpoint => typeof endpoint === 'object' ? getNodeId(endpoint) : endpoint;

  const circularSlotsByNodeIndex = computeCrossingMinimizedCircularOrder(
    nodes,
    edges,
    getNodeId,
    getEndpointId,
    hp.CROSSING_MAX_ITERATIONS,
    hp
  );
  const nodeCount = nodes.length;

  const totalCircumferenceNeeded = nodes.reduce((sum, node) => sum + calculateNodeWidth(node, hp) + hp.MIN_NODE_GAP, 0);
  const circleRadius = nodeCount === 1 ? 0 : Math.max(hp.MIN_CIRCLE_RADIUS, totalCircumferenceNeeded / (2 * Math.PI));
  const angleStep = (2 * Math.PI) / Math.max(1, nodeCount);

  nodes.forEach((node, index) => {
    const slotIndex = circularSlotsByNodeIndex[index];
    node.x = canvasWidth / 2 + circleRadius * Math.cos(slotIndex * angleStep);
    node.y = canvasHeight / 2 + circleRadius * Math.sin(slotIndex * angleStep);
  });
}

function computeCrossingMinimizedCircularOrder(nodes, edges, getNodeId, getEndpointId, maxIterations, hp) {
  const nodeCount = nodes.length;
  if (nodeCount < 4 || edges.length === 0) return nodes.map((_, i) => i);

  const nodeIndexById = new Map(nodes.map((node, index) => [getNodeId(node), index]));
  const adjacencyList = Array.from({ length: nodeCount }, () => []);
  const uniqueEdgePairs = [];
  const seenEdgeKeys = new Set();

  edges.forEach(edge => {
    const sourceIdx = nodeIndexById.get(getEndpointId(edge.source));
    const targetIdx = nodeIndexById.get(getEndpointId(edge.target));
    if (sourceIdx === undefined || targetIdx === undefined || sourceIdx === targetIdx) return;

    const edgeKey = sourceIdx < targetIdx ? `${sourceIdx},${targetIdx}` : `${targetIdx},${sourceIdx}`;
    if (seenEdgeKeys.has(edgeKey)) return;

    seenEdgeKeys.add(edgeKey);
    uniqueEdgePairs.push([sourceIdx, targetIdx]);
    adjacencyList[sourceIdx].push(targetIdx);
    adjacencyList[targetIdx].push(sourceIdx);
  });

  const nodesSortedByDegree = [...Array(nodeCount).keys()].sort((a, b) => adjacencyList[b].length - adjacencyList[a].length);
  const visitedNodes = new Array(nodeCount).fill(false);
  const initialNodeOrder = [];

  for (const startNodeIdx of nodesSortedByDegree) {
    if (visitedNodes[startNodeIdx]) continue;
    const bfsQueue = [startNodeIdx];
    visitedNodes[startNodeIdx] = true;

    while (bfsQueue.length > 0) {
      const currentNodeIdx = bfsQueue.shift();
      initialNodeOrder.push(currentNodeIdx);
      for (const neighborIdx of adjacencyList[currentNodeIdx]) {
        if (!visitedNodes[neighborIdx]) {
          visitedNodes[neighborIdx] = true;
          bfsQueue.push(neighborIdx);
        }
      }
    }
  }

  const slotByNodeIndex = new Array(nodeCount);
  initialNodeOrder.forEach((nodeIndex, slot) => { slotByNodeIndex[nodeIndex] = slot; });

  const countChordCrossings = () => {
    let crossings = 0;
    for (let i = 0; i < uniqueEdgePairs.length; i++) {
      let [slotA, slotB] = [slotByNodeIndex[uniqueEdgePairs[i][0]], slotByNodeIndex[uniqueEdgePairs[i][1]]];
      if (slotA > slotB) [slotA, slotB] = [slotB, slotA];

      for (let j = i + 1; j < uniqueEdgePairs.length; j++) {
        let [slotC, slotD] = [slotByNodeIndex[uniqueEdgePairs[j][0]], slotByNodeIndex[uniqueEdgePairs[j][1]]];
        if (slotC > slotD) [slotC, slotD] = [slotD, slotC];

        if ((slotA < slotC && slotC < slotB && slotB < slotD) || (slotC < slotA && slotA < slotD && slotD < slotB)) {
          crossings++;
        }
      }
    }
    return crossings;
  };

  let currentCrossings = countChordCrossings();
  let minCrossings = currentCrossings;
  let bestSlotAssignment = slotByNodeIndex.slice();
  let temperature = hp.INITIAL_TEMPERATURE;
  const coolingFactor = Math.pow(hp.FINAL_TEMPERATURE / hp.INITIAL_TEMPERATURE, 1 / maxIterations);

  for (let iteration = 0; iteration < maxIterations && minCrossings > 0; iteration++) {
    const nodeIdxA = Math.floor(Math.random() * nodeCount);
    let nodeIdxB = Math.floor(Math.random() * (nodeCount - 1));
    if (nodeIdxB >= nodeIdxA) nodeIdxB++;

    [slotByNodeIndex[nodeIdxA], slotByNodeIndex[nodeIdxB]] = [slotByNodeIndex[nodeIdxB], slotByNodeIndex[nodeIdxA]];
    const candidateCrossings = countChordCrossings();
    const crossingDelta = candidateCrossings - currentCrossings;

    if (crossingDelta <= 0 || Math.random() < Math.exp(-crossingDelta / temperature)) {
      currentCrossings = candidateCrossings;
      if (currentCrossings < minCrossings) {
        minCrossings = currentCrossings;
        bestSlotAssignment = slotByNodeIndex.slice();
      }
    } else {
      [slotByNodeIndex[nodeIdxA], slotByNodeIndex[nodeIdxB]] = [slotByNodeIndex[nodeIdxB], slotByNodeIndex[nodeIdxA]];
    }
    temperature *= coolingFactor;
  }

  return bestSlotAssignment;
}

// ============================================================================
// 4. GRAPH DATA PARSING & STATE MANAGEMENT
// ============================================================================

function resolveGraphTypeFlags(dsType = '', extraInputs = {}) {
  const lower = dsType.toLowerCase();
  let isDirected = lower.includes('directed') && !lower.includes('undirected');
  let isWeighted = lower.includes('weighted') && !lower.includes('unweighted');

  if (extraInputs && typeof extraInputs === 'object') {
    for (const [k, v] of Object.entries(extraInputs)) {
      const keyLower = k.toLowerCase();
      if (keyLower === 'directed') isDirected = Boolean(v);
      if (keyLower === 'weighted') isWeighted = Boolean(v);
    }
  }
  return { isDirected, isWeighted };
}

function refreshEdgeFlags(graphData) {
  const { nodes, edges, isDirected } = graphData;
  const nodeByIdMap = new Map(nodes.map(n => [String(n.id), n]));

  edges.forEach(edge => {
    const sId = typeof edge.source === 'object' ? String(edge.source.id) : String(edge.source);
    const tId = typeof edge.target === 'object' ? String(edge.target.id) : String(edge.target);
    edge.source = nodeByIdMap.get(sId) || edge.source;
    edge.target = nodeByIdMap.get(tId) || edge.target;
  });

  const edgeLookupSet = new Set(
    edges.map(e => `${typeof e.source === 'object' ? e.source.id : e.source}-${typeof e.target === 'object' ? e.target.id : e.target}`)
  );

  edges.forEach(edge => {
    const sId = typeof edge.source === 'object' ? edge.source.id : edge.source;
    const tId = typeof edge.target === 'object' ? edge.target.id : edge.target;
    edge.selfLoop = (sId === tId);
    edge.bidirectional = Boolean(isDirected && !edge.selfLoop && edgeLookupSet.has(`${tId}-${sId}`));
  });
}

function allocateNextNodeId(graphData) {
  if (typeof graphData._nextNodeId !== 'number') {
    const maxExisting = (graphData.nodes || []).reduce((max, n) => {
      const num = Number(n.id);
      return Number.isInteger(num) && num > max ? num : max;
    }, -1);
    graphData._nextNodeId = maxExisting + 1;
  }
  return graphData._nextNodeId++;
}

function generateDefaultNodeLabel(nodes) {
  if (!nodes || nodes.length === 0) return '0';

  const labels = nodes.map(n => String(n.label !== undefined ? n.label : n.id).trim());
  const allInts = labels.every(l => /^-?\d+$/.test(l));

  // 1. All integer labels -> next ascending integer after max
  if (allInts) {
    const maxVal = Math.max(...labels.map(Number));
    return String(maxVal + 1);
  }

  // 2. All alphabetic strings -> increment last character (e.g. A -> B -> C, Z -> AA)
  const allAlpha = labels.every(l => /^[a-zA-Z]+$/.test(l));
  if (allAlpha) {
    const sorted = [...labels].sort((a, b) => a.length - b.length || a.localeCompare(b));
    const last = sorted[sorted.length - 1];
    const isLower = last === last.toLowerCase();
    const baseCode = isLower ? 97 : 65;

    const chars = last.split('').map(c => c.toUpperCase().charCodeAt(0) - 65);
    let carry = 1;
    for (let i = chars.length - 1; i >= 0 && carry > 0; i--) {
      const sum = chars[i] + carry;
      chars[i] = sum % 26;
      carry = Math.floor(sum / 26);
    }
    if (carry > 0) chars.unshift(0);
    const candidate = chars.map(c => String.fromCharCode(baseCode + c)).join('');
    if (!labels.includes(candidate)) return candidate;
  }

  // 3. Hybrid labels -> random short unique identifier
  const existingSet = new Set(labels);
  const alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
  for (let attempt = 0; attempt < 100; attempt++) {
    const candidate =
      alphabet[Math.floor(Math.random() * 26)] +
      alphabet[Math.floor(Math.random() * alphabet.length)];
    if (!existingSet.has(candidate)) return candidate;
  }
  return `N${nodes.length}`;
}

/* ---------- Standalone Graph Input Parser ---------- */

function parseEdges(edgesInput) {
  const trimmed = edgesInput.trim();

  if (trimmed.startsWith('{')) {
    return parsePythonAdjacencyDict(trimmed);
  }
  if (trimmed.startsWith('[')) {
    const inner = stripOuter(trimmed, '[', ']');
    if (inner === '') return [];

    const topLevelTokens = tokeniseTopLevel(inner);
    const looksLikeTupleList = topLevelTokens.some(t => t.startsWith('('));
    const looksLikeMatrix = topLevelTokens.some(t => t.startsWith('['));

    if (looksLikeTupleList) return parsePythonEdgeList(trimmed);
    if (looksLikeMatrix) return parseAdjacencyMatrix(trimmed);
    return parseCompactEdges(trimmed);
  }
  return parseCompactEdges(trimmed);
}

function tokeniseTopLevel(input, delimiter = ',') {
  const result = [];
  let depth = 0;
  let current = '';
  for (const char of input) {
    if (char === '(' || char === '[' || char === '{') depth++;
    if (char === ')' || char === ']' || char === '}') depth--;
    if (char === delimiter && depth === 0) {
      if (current.trim()) result.push(current.trim());
      current = '';
    } else {
      current += char;
    }
  }
  if (current.trim()) result.push(current.trim());
  return result;
}

function stripOuter(s, open, close) {
  s = s.trim();
  if (s.startsWith(open) && s.endsWith(close)) return s.slice(1, -1).trim();
  return s;
}

function parseNode(token) {
  token = token.trim();
  if ((token.startsWith('"') && token.endsWith('"')) ||
    (token.startsWith("'") && token.endsWith("'"))) {
    return token.slice(1, -1);
  }
  return token;
}

function parseWeight(token) {
  if (token === undefined || token === null) return 1;
  const w = parseFloat(token.trim());
  return isNaN(w) ? 1 : w;
}

function parsePythonEdgeList(input) {
  const edges = [];
  const inner = stripOuter(input, '[', ']');
  if (!inner) return edges;

  const tuples = tokeniseTopLevel(inner);

  for (const tuple of tuples) {
    const t = tuple.trim();
    if (!t.startsWith('(')) { console.error('Expected tuple, got:', t); continue; }
    const tupleInner = stripOuter(t, '(', ')');
    const parts = tokeniseTopLevel(tupleInner);

    if (parts.length === 1 && parts[0]) {
      edges.push({ source: parseNode(parts[0]), target: null, weight: null });
      continue;
    }
    if (parts.length < 2) { console.error('Edge tuple needs >= 2 elements:', t); continue; }

    const source = parseNode(parts[0]);
    const target = parseNode(parts[1]);
    const weight = parts.length >= 3 ? parseWeight(parts[2]) : 1;

    edges.push({ source, target, weight });
  }

  return edges;
}

function parseNeighbourEntry(entry) {
  entry = entry.trim();
  if (entry.startsWith('(')) {
    const inner = stripOuter(entry, '(', ')');
    const parts = tokeniseTopLevel(inner);
    if (parts.length >= 2) {
      return { target: parseNode(parts[0]), weight: parseWeight(parts[1]) };
    }
    if (parts.length === 1) {
      return { target: parseNode(parts[0]), weight: 1 };
    }
  }
  return { target: parseNode(entry), weight: 1 };
}

function parsePythonAdjacencyDict(input) {
  const edges = [];
  const inner = stripOuter(input, '{', '}');
  if (!inner) return edges;

  const pairs = tokeniseTopLevel(inner);

  for (const pair of pairs) {
    let colonIdx = -1;
    let depth = 0;
    for (let i = 0; i < pair.length; i++) {
      const c = pair[i];
      if (c === '(' || c === '[' || c === '{') depth++;
      if (c === ')' || c === ']' || c === '}') depth--;
      if (c === ':' && depth === 0) { colonIdx = i; break; }
    }
    if (colonIdx === -1) { console.error('Invalid adjacency entry:', pair); continue; }

    const source = parseNode(pair.slice(0, colonIdx).trim());
    const valueStr = pair.slice(colonIdx + 1).trim();

    if (valueStr.startsWith('[')) {
      const listInner = stripOuter(valueStr, '[', ']');
      if (!listInner) {
        edges.push({ source, target: null, weight: null });
        continue;
      }
      const neighbours = tokeniseTopLevel(listInner);
      for (const nb of neighbours) {
        const { target, weight } = parseNeighbourEntry(nb);
        edges.push({ source, target, weight });
      }
    } else {
      const { target, weight } = parseNeighbourEntry(valueStr);
      edges.push({ source, target, weight });
    }
  }

  return edges;
}

function parseAdjacencyMatrix(matrixInput) {
  const trimmed = matrixInput.trim();
  const outer = stripOuter(trimmed, '[', ']');
  const rowTokens = tokeniseTopLevel(outer);

  if (rowTokens.length === 0) {
    throw new Error('Invalid adjacency matrix: no rows found.');
  }

  const rows = rowTokens.map(rowToken => {
    const t = rowToken.trim();
    if (!t.startsWith('[') || !t.endsWith(']')) {
      throw new Error(`Invalid adjacency matrix: expected a row like "[1, 0, 2]", got "${t}".`);
    }
    const inner = stripOuter(t, '[', ']');
    const cellTokens = inner === '' ? [] : tokeniseTopLevel(inner);

    return cellTokens.map(cell => {
      const c = cell.trim();
      if (!/^-?\d+(\.\d+)?$/.test(c)) {
        throw new Error(`Invalid adjacency matrix: non-numeric value "${c}" found. Only numeric vertices/weights are allowed.`);
      }
      return parseFloat(c);
    });
  });

  const n = rows.length;
  for (const row of rows) {
    if (row.length !== n) {
      throw new Error(`Invalid adjacency matrix: must be square (found ${n} rows but a row with ${row.length} columns).`);
    }
  }

  const edges = [];
  for (let i = 0; i < n; i++) {
    let hasEdgeInRow = false;
    for (let j = 0; j < n; j++) {
      const value = rows[i][j];
      if (value === 0) continue;
      hasEdgeInRow = true;
      edges.push({ source: i, target: j, weight: value });
    }
    if (!hasEdgeInRow) {
      edges.push({ source: i, target: null, weight: null });
    }
  }

  return edges;
}

function parseCompactEdges(edgesInput) {
  const edgeFormat = /^([a-zA-Z0-9])([a-zA-Z0-9])(-?\d*\.?\d*)$/;
  const vertexFormat = /^[a-zA-Z0-9]$/;

  return tokeniseTopLevel(edgesInput).map(edge => {
    edge = edge.trim();
    let source, target, weight;

    if (edgeFormat.test(edge)) {
      const match = edge.match(edgeFormat);
      source = match[1];
      target = match[2];
      weight = parseFloat(match[3]);
      if (isNaN(weight)) weight = 1;
    } else if (vertexFormat.test(edge)) {
      source = edge;
      target = null;
      weight = null;
    } else {
      console.error('Invalid edge format:', edge);
      return null;
    }

    return { source, target, weight };
  }).filter(Boolean);
}

function parseGraphInput(rawInput, dsType = 'Graph', extraInputs = {}) {
  const { isDirected, isWeighted } = resolveGraphTypeFlags(dsType, extraInputs);

  const text = (rawInput || '').trim();
  const nodesByTokenMap = new Map();
  const nodes = [];
  const edges = [];
  const seenUndirectedPairs = new Set();
  let nextInternalId = 0;

  const ensureNode = (tokenVal) => {
    if (tokenVal === null || tokenVal === undefined) return null;
    const cleanLabel = String(tokenVal).trim();
    if (!cleanLabel) return null;
    if (!nodesByTokenMap.has(cleanLabel)) {
      const nodeObj = {
        id: nextInternalId++,
        label: cleanLabel,
        x: 0,
        y: 0
      };
      nodesByTokenMap.set(cleanLabel, nodeObj);
      nodes.push(nodeObj);
    }
    return nodesByTokenMap.get(cleanLabel);
  };

  if (text) {
    let rawEdges = [];
    try {
      rawEdges = parseEdges(text);
    } catch (err) {
      console.error(err);
    }

    for (const item of rawEdges) {
      const uNode = ensureNode(item.source);
      if (item.target === null || item.target === undefined) continue;
      const vNode = ensureNode(item.target);
      if (!uNode || !vNode) continue;

      if (!isDirected) {
        const pairKey = uNode.id <= vNode.id
          ? `${uNode.id}-${vNode.id}`
          : `${vNode.id}-${uNode.id}`;
        if (seenUndirectedPairs.has(pairKey)) continue;
        seenUndirectedPairs.add(pairKey);
      }

      const parsedW = (item.weight !== undefined && item.weight !== null && !Number.isNaN(Number(item.weight)))
        ? Number(item.weight)
        : 1;
      edges.push({ source: uNode, target: vNode, weight: parsedW });
    }
  }

  const graphData = { nodes, edges, isDirected, isWeighted, _nextNodeId: nextInternalId };
  refreshEdgeFlags(graphData);
  return graphData;
}

// --- Graph Copy / Export Formatters ---
function formatGraphAsEdgeList(graphData) {
  const { nodes, edges, isDirected, isWeighted } = graphData;
  const connectedIds = new Set();
  const op = isDirected ? '->' : '-';

  const edgeStrings = edges.map(e => {
    connectedIds.add(e.source.id);
    connectedIds.add(e.target.id);
    const u = e.source.label ?? e.source.id;
    const v = e.target.label ?? e.target.id;
    const w = isWeighted ? `:${e.weight ?? 1}` : '';
    return `${u}${op}${v}${w}`;
  });

  const isolatedStrings = nodes
    .filter(n => !connectedIds.has(n.id))
    .map(n => String(n.label ?? n.id));

  return [...edgeStrings, ...isolatedStrings].join(', ');
}

function formatGraphAsAdjacencyList(graphData) {
  const { nodes, edges, isDirected, isWeighted } = graphData;
  const adj = new Map(nodes.map(n => [n.id, []]));

  edges.forEach(e => {
    const uId = e.source.id;
    const vId = e.target.id;
    const uLabel = e.source.label ?? uId;
    const vLabel = e.target.label ?? vId;
    const w = e.weight ?? 1;

    if (adj.has(uId)) {
      adj.get(uId).push(isWeighted ? [vLabel, w] : vLabel);
    }
    if (!isDirected && uId !== vId && adj.has(vId)) {
      adj.get(vId).push(isWeighted ? [uLabel, w] : uLabel);
    }
  });

  const resultObj = {};
  nodes.forEach(n => {
    const key = String(n.label ?? n.id);
    const finalKey = Object.prototype.hasOwnProperty.call(resultObj, key) ? `${key}#${n.id}` : key;
    resultObj[finalKey] = adj.get(n.id) || [];
  });
  return JSON.stringify(resultObj, null, 2);
}

function formatGraphAsAdjacencyMatrix(graphData) {
  const { nodes, edges, isDirected, isWeighted } = graphData;
  const n = nodes.length;
  const idxById = new Map(nodes.map((node, i) => [node.id, i]));
  const matrix = Array.from({ length: n }, () => new Array(n).fill(0));

  edges.forEach(e => {
    const i = idxById.get(e.source.id);
    const j = idxById.get(e.target.id);
    if (i === undefined || j === undefined) return;
    const val = isWeighted ? (e.weight ?? 1) : 1;
    matrix[i][j] = val;
    if (!isDirected) matrix[j][i] = val;
  });

  return JSON.stringify(matrix);
}

function formatGraphAsJsonWithAttributes(graphData) {
  return JSON.stringify({
    isDirected: Boolean(graphData.isDirected),
    isWeighted: Boolean(graphData.isWeighted),
    nodes: graphData.nodes.map(n => ({
      id: n.id,
      label: n.label ?? String(n.id),
      x: Math.round(n.x),
      y: Math.round(n.y)
    })),
    edges: graphData.edges.map(e => ({
      source: e.source.id,
      target: e.target.id,
      weight: e.weight ?? 1
    }))
  }, null, 2);
}

export function getContainerGraphData(containerEl) {
  if (!containerEl) return { nodes: [], edges: [], isDirected: false, isWeighted: false };

  const rawInput = containerEl.getAttribute('userInput') || containerEl.userInput || '';
  const dsType = containerEl.dataset.dsType || 'Graph';
  let extraInputs = containerEl.dsInputs || {};
  if ((!extraInputs || Object.keys(extraInputs).length === 0) && containerEl.dataset.dsInputs) {
    try {
      extraInputs = JSON.parse(containerEl.dataset.dsInputs);
    } catch { }
  }
  const serializedInputs = JSON.stringify(extraInputs);

  if (
    !containerEl._graphData ||
    containerEl._lastParsedGraphInput !== rawInput ||
    containerEl._lastParsedGraphInputsJson !== serializedInputs
  ) {
    const parsed = parseGraphInput(rawInput, dsType, extraInputs);
    const canvas = containerEl.querySelector('canvas');
    const w = (canvas && canvas.clientWidth) ? canvas.clientWidth : 800;
    const h = (canvas && canvas.clientHeight) ? canvas.clientHeight : 600;

    applyCircularNodeLayout(parsed.nodes, w, h, parsed.edges);
    containerEl._graphData = parsed;
    containerEl._lastParsedGraphInput = rawInput;
    containerEl._lastParsedGraphInputsJson = serializedInputs;
  }

  return containerEl._graphData;
}

export function syncGraphDataToContainer(containerEl, graphData) {
  if (!containerEl || !graphData) return;
  refreshEdgeFlags(graphData);

  const adjEntries = graphData.nodes.map(n => {
    const uLabel = String(n.label ?? n.id);
    const outgoing = graphData.edges.filter(e => {
      const sId = typeof e.source === 'object' ? e.source.id : e.source;
      return sId === n.id;
    });
    const neighborTokens = outgoing.map(e => {
      const vNode = typeof e.target === 'object' ? e.target : graphData.nodes.find(nd => nd.id === e.target);
      const vLabel = vNode ? String(vNode.label ?? vNode.id) : String(e.target);
      return graphData.isWeighted ? `(${vLabel}, ${e.weight ?? 1})` : `${vLabel}`;
    });
    return `${uLabel}: [${neighborTokens.join(', ')}]`;
  });

  const serialized = adjEntries.length > 0 ? `{${adjEntries.join(', ')}}` : '';
  containerEl._graphData = graphData;
  containerEl._lastParsedGraphInput = serialized;

  const extraInputs = containerEl.dsInputs || {};
  containerEl._lastParsedGraphInputsJson = JSON.stringify(extraInputs);

  containerEl.userInput = serialized;
  containerEl.setAttribute('userInput', serialized);

  if (typeof window.updateDsHeaderWarningState === 'function') {
    window.updateDsHeaderWarningState();
  }
  if (typeof window.updateMetadataUI === 'function') {
    window.updateMetadataUI();
  }
}

// ============================================================================
// 5. CORE CANVAS GRAPH RENDERING PIPELINE
// ============================================================================

function drawDirectedArrowhead(ctx, x, y, angle, isSelfLoop, color, hp) {
  const scale = hp.ARROW_SCALE;
  const refX = isSelfLoop ? hp.ARROW_SELF_LOOP_REF_X : hp.ARROW_REF_X;
  const refY = isSelfLoop ? hp.ARROW_SELF_LOOP_REF_Y : hp.ARROW_REF_Y;

  ctx.save();
  ctx.translate(x, y);
  ctx.rotate(angle);
  ctx.scale(scale, scale);
  ctx.translate(-refX, -refY);

  ctx.beginPath();
  ctx.moveTo(0, -5);
  ctx.lineTo(10, 0);
  ctx.lineTo(0, 5);
  ctx.closePath();
  ctx.fillStyle = color;
  ctx.fill();
  ctx.restore();
}

export function drawGraph(containerEl, camera = { x: 0, y: 0, z: 1 }, customHyperparameters = {}) {
  if (!containerEl) return;
  const canvas = containerEl.querySelector('canvas');
  if (!canvas) return;

  const hp = resolveStyleHyperparameters({
    ...GRAPH_HYPERPARAMETERS,
    ...customHyperparameters,
  });

  const ctx = canvas.getContext('2d');
  const dpr = Math.min(2, window.devicePixelRatio || 1);
  const graphData = getContainerGraphData(containerEl);
  const { nodes, edges, isDirected, isWeighted } = graphData;

  refreshEdgeFlags(graphData);

  const hoveredEdge = containerEl._hoveredEdge || null;
  const draggedNode = containerEl._dragState ? containerEl._dragState.node : null;
  const simStep = containerEl._simStep || null;

  ctx.save();
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  ctx.scale(camera.z, camera.z);
  ctx.translate(camera.x, camera.y);

  let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
  const expandBounds = (x1, y1, x2, y2) => {
    if (x1 < minX) minX = x1;
    if (y1 < minY) minY = y1;
    if (x2 > maxX) maxX = x2;
    if (y2 > maxY) maxY = y2;
  };

  // 1. Render visible edges & cache Path2D objects for hit-buffer detection
  const renderedEdges = [];
  for (const edge of edges) {
    if (!edge.source || !edge.target) continue;
    const geom = calculateEdgePathAndLabelPosition(edge, hp);
    const path2D = new Path2D(geom.svgPath);
    edge._path2D = path2D;
    edge._geom = geom;

    const isHovered = (hoveredEdge === edge);
    const sId = String(typeof edge.source === 'object' ? edge.source.id : edge.source);
    const tId = String(typeof edge.target === 'object' ? edge.target.id : edge.target);

    const matchesEdgePair = (pair) => {
      if (!Array.isArray(pair) || pair.length < 2) return false;
      const u = String(pair[0]);
      const v = String(pair[1]);
      return (u === sId && v === tId) || (!isDirected && u === tId && v === sId);
    };

    const isActiveEdge = simStep && simStep.activeEdge && matchesEdgePair(simStep.activeEdge);
    const isVisitedEdge = simStep && Array.isArray(simStep.visitedEdges) && simStep.visitedEdges.some(matchesEdgePair);
    const isCandidateEdge = simStep?.interaction?.candidateEdges && simStep.interaction.candidateEdges.some(matchesEdgePair);

    let strokeColor = hp.EDGE_STROKE;
    if (isCandidateEdge) {
      strokeColor = hp.CANDIDATE;
    } else if (isHovered) {
      strokeColor = hp.EDGE_HOVER_STROKE;
    } else if (isActiveEdge) {
      strokeColor = hp.CURRENT_FILL;
    } else if (isVisitedEdge) {
      strokeColor = hp.EDGE_VISITED;
    }

    ctx.save();
    ctx.globalAlpha = hp.DEFAULT_ALPHA;
    ctx.strokeStyle = strokeColor;
    ctx.lineWidth = hp.EDGE_STROKE_WIDTH;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    ctx.stroke(path2D);
    ctx.restore();

    if (isDirected) {
      drawDirectedArrowhead(ctx, geom.arrowX, geom.arrowY, geom.arrowAngle, geom.isSelfLoop, strokeColor, hp);
    }

    if (geom.bounds) {
      const pad = hp.BOUNDS_PADDING;
      expandBounds(geom.bounds.minX - pad, geom.bounds.minY - pad, geom.bounds.maxX + pad, geom.bounds.maxY + pad);
    }
    renderedEdges.push({ edge, geom, strokeColor });
  }

  // 1b. Render live preview edge while double-click dragging from a source node
  const edgeCreateState = containerEl._edgeCreateState;
  if (edgeCreateState && edgeCreateState.sourceNode) {
    const src = edgeCreateState.sourceNode;
    const tgtNode = edgeCreateState.hoverTargetNode;
    const endX = tgtNode ? tgtNode.x : edgeCreateState.currX;
    const endY = tgtNode ? tgtNode.y : edgeCreateState.currY;

    ctx.save();
    ctx.strokeStyle = hp.EDGE_HOVER_STROKE;
    ctx.lineWidth = hp.EDGE_STROKE_WIDTH;
    ctx.setLineDash([8, 6]);
    ctx.lineCap = 'round';
    ctx.beginPath();

    if (tgtNode && tgtNode === src) {
      const r = hp.SELF_LOOP_RADIUS;
      ctx.arc(src.x + hp.SELF_LOOP_OFFSET_X, src.y + hp.SELF_LOOP_OFFSET_Y, r, 0, Math.PI * 2);
    } else {
      ctx.moveTo(src.x, src.y);
      ctx.lineTo(endX, endY);
    }
    ctx.stroke();
    ctx.restore();

    if (isDirected && (!tgtNode || tgtNode !== src)) {
      const angle = Math.atan2(endY - src.y, endX - src.x);
      drawDirectedArrowhead(ctx, endX, endY, angle, false, hp.EDGE_HOVER_STROKE, hp);
    }
  }

  // 2. Render nodes (rounded rectangles) and node labels
  const nodeHitBoxes = [];
  for (let i = 0; i < nodes.length; i++) {
    const node = nodes[i];
    const w = calculateNodeWidth(node, hp);
    const h = hp.NODE_HEIGHT;
    const x = node.x - w / 2;
    const y = node.y - h / 2;
    node._width = w;
    node._height = h;

    const nodeIdStr = String(node.id);
    const isCandidateNode =
      simStep?.interaction?.candidateNodeIds &&
      simStep.interaction.candidateNodeIds.map(String).includes(nodeIdStr);
    const isSourceNode =
      simStep?.interaction?.sourceNodeId !== undefined &&
      String(simStep.interaction.sourceNodeId) === nodeIdStr;

    let fillColor = hp.NODE_FILL;

    if (draggedNode === node) {
      fillColor = hp.NODE_DRAG_FILL;
    } else if (isSourceNode) {
      fillColor = hp.SOURCE_NODE; // Highlights the "from" vertex during manual choice!
    } else if (isCandidateNode) {
      fillColor = hp.CANDIDATE;   // Highlights the selectable "to" vertices!
    } else if (simStep) {
      const isVisited = Array.isArray(simStep.visitedNodes) && simStep.visitedNodes.map(String).includes(nodeIdStr);
      const isEndpointOfActiveEdge =
        Array.isArray(simStep.activeEdge) && simStep.activeEdge.map(String).includes(nodeIdStr);
      const isInActiveNodes =
        Array.isArray(simStep.activeNodeIds) && simStep.activeNodeIds.map(String).includes(nodeIdStr);

      if (String(simStep.foundNodeId) === nodeIdStr || simStep.foundIndex === i) {
        fillColor = hp.FOUND_FILL;
      } else if (
        String(simStep.activeNodeId) === nodeIdStr ||
        isInActiveNodes ||
        isEndpointOfActiveEdge ||
        simStep.activeIndex === i
      ) {
        fillColor = hp.CURRENT_FILL;
      } else if (isVisited) {
        fillColor = hp.CHECKED_COLOR;
      }
    }

    ctx.save();
    ctx.globalAlpha = hp.DEFAULT_ALPHA;
    ctx.beginPath();
    if (typeof ctx.roundRect === 'function') {
      ctx.roundRect(x, y, w, h, hp.NODE_CORNER_RADIUS);
    } else {
      ctx.rect(x, y, w, h);
    }
    ctx.fillStyle = fillColor;
    ctx.fill();
    ctx.lineWidth = hp.NODE_STROKE_WIDTH;
    ctx.strokeStyle = hp.NODE_STROKE;
    ctx.stroke();

    // Node Label
    const displayText = String(node.label !== undefined ? node.label : node.id);
    ctx.font = getNodeFont(hp);
    ctx.fillStyle = hp.TEXT_DARK;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(displayText, node.x, node.y);
    ctx.restore();

    nodeHitBoxes.push({ index: i, node, x, y, w, h });
    const pad = hp.BOUNDS_PADDING;
    expandBounds(x - pad, y - pad, x + w + pad, y + h + pad);

    ctx.lineWidth = hp.NODE_STROKE_WIDTH;
    ctx.strokeStyle = isCandidateNode ? hp.CANDIDATE : hp.NODE_STROKE;
    ctx.stroke();
  }

  // 3. Render edge weight labels on top (Border matches edge highlight state)
  const weightHitBoxes = [];
  if (isWeighted) {
    for (const { edge, geom, strokeColor } of renderedEdges) {
      if (edge.weight === undefined || edge.weight === null) continue;
      const weightText = String(edge.weight);

      ctx.save();
      ctx.font = getEdgeLabelFont(hp);
      const textWidth = ctx.measureText(weightText).width;
      const pillW = Math.max(24, textWidth + hp.WEIGHT_PILL_PADDING_X * 2);
      const pillH = hp.WEIGHT_PILL_HEIGHT;
      const pillX = geom.labelX - pillW / 2;
      const pillY = geom.labelY - pillH / 2;

      ctx.beginPath();
      if (typeof ctx.roundRect === 'function') {
        ctx.roundRect(pillX, pillY, pillW, pillH, hp.WEIGHT_PILL_RADIUS);
      } else {
        ctx.rect(pillX, pillY, pillW, pillH);
      }
      ctx.fillStyle = hp.WEIGHT_BG;
      ctx.fill();

      // Border stroke matches the edge's active, visited, hovered, or default color
      ctx.lineWidth = hp.WEIGHT_PILL_STROKE_WIDTH;
      ctx.strokeStyle = strokeColor;
      ctx.stroke();

      // Text color (remains constant)
      ctx.fillStyle = hp.TEXT_BRIGHT;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(weightText, geom.labelX, geom.labelY);
      ctx.restore();

      weightHitBoxes.push({ edge, x: pillX, y: pillY, w: pillW, h: pillH });
    }
  }

  ctx.restore();

  containerEl._nodeHitBoxes = nodeHitBoxes;
  containerEl._weightHitBoxes = weightHitBoxes;
  if (minX !== Infinity) {
    containerEl._structureBounds = { minX, minY, maxX, maxY };
  } else {
    containerEl._structureBounds = null;
  }
}

// ============================================================================
// 6. CANVAS INTERACTION HANDLERS (DRAG, WEIGHT EDIT, NODE/EDGE CONTEXT MENUS)
// ============================================================================

let graphOptionsModal = null;
function getGraphModal() {
  if (!graphOptionsModal && typeof window.FloatingWindow === 'function') {
    graphOptionsModal = new window.FloatingWindow('Graph Options');
  }
  return graphOptionsModal;
}

function setModalTitle(modal, title) {
  const titleEl = modal?.overlay?.querySelector('.modal-header span');
  if (titleEl) titleEl.textContent = title;
}

export function setupGraphInteractions(containerEl, requestRender) {
  if (!containerEl) return;
  const canvas = containerEl.querySelector('canvas');
  if (!canvas) return;

  const hitTestCtx = document.createElement('canvas').getContext('2d');

  const screenToWorld = (clientX, clientY) => {
    const rect = canvas.getBoundingClientRect();
    const cam = containerEl._camera || { x: 0, y: 0, z: 1 };
    const sx = clientX - rect.left;
    const sy = clientY - rect.top;
    return {
      x: sx / cam.z - cam.x,
      y: sy / cam.z - cam.y
    };
  };

  const hitTestWeightBox = (wx, wy) => {
    const graphData = getContainerGraphData(containerEl);
    if (!graphData.isWeighted) return null;
    const boxes = containerEl._weightHitBoxes || [];
    for (let i = boxes.length - 1; i >= 0; i--) {
      const b = boxes[i];
      if (wx >= b.x && wx <= b.x + b.w && wy >= b.y && wy <= b.y + b.h) {
        return b.edge;
      }
    }
    return null;
  };

  const hitTestNode = (wx, wy) => {
    const boxes = containerEl._nodeHitBoxes || [];
    for (let i = boxes.length - 1; i >= 0; i--) {
      const b = boxes[i];
      const dx = Math.abs(wx - b.node.x);
      const dy = Math.abs(wy - b.node.y);
      const halfW = b.w / 2;
      const halfH = b.h / 2;

      if (dx > halfW || dy > halfH) continue;

      const r = Math.min(GRAPH_HYPERPARAMETERS.NODE_CORNER_RADIUS, halfW, halfH);
      const innerW = halfW - r;
      const innerH = halfH - r;
      if (dx <= innerW || dy <= innerH) return b.node;

      const cornerDx = dx - innerW;
      const cornerDy = dy - innerH;
      if (cornerDx * cornerDx + cornerDy * cornerDy <= r * r) {
        return b.node;
      }
    }
    return null;
  };

  const hitTestEdge = (wx, wy) => {
    const graphData = getContainerGraphData(containerEl);
    const edges = graphData.edges || [];
    hitTestCtx.save();
    hitTestCtx.setTransform(1, 0, 0, 1, 0, 0);
    hitTestCtx.lineWidth = GRAPH_HYPERPARAMETERS.EDGE_HIT_BUFFER_WIDTH;
    hitTestCtx.lineCap = 'round';
    hitTestCtx.lineJoin = 'round';

    for (let i = edges.length - 1; i >= 0; i--) {
      const edge = edges[i];
      if (edge._path2D && hitTestCtx.isPointInStroke(edge._path2D, wx, wy)) {
        hitTestCtx.restore();
        return edge;
      }
    }
    hitTestCtx.restore();
    return null;
  };

  // --- Floating Window Menus ---
  const openEditWeightModal = (edge) => {
    const modal = getGraphModal();
    if (!modal) return;
    const uLabel = edge.source.label ?? edge.source.id;
    const vLabel = edge.target.label ?? edge.target.id;
    setModalTitle(modal, `Edit Weight (${uLabel} → ${vLabel})`);
    modal.setContent(`
      <div style="display: flex; flex-direction: column; gap: 0.5rem;">
        <input type="number" step="any" id="fw-graph-weight-input" class="param-input-field" value="${edge.weight ?? 1}" placeholder="Enter edge weight" />
        <button type="button" id="fw-graph-weight-save" class="vscode-btn-secondary" style="width: 100%;">Save Weight</button>
      </div>
    `);
    modal.open();

    const inputEl = modal.body.querySelector('#fw-graph-weight-input');
    const saveBtn = modal.body.querySelector('#fw-graph-weight-save');
    if (inputEl) {
      requestAnimationFrame(() => { inputEl.focus(); inputEl.select(); });
    }
    const commitWeight = () => {
      const parsed = Number(inputEl.value.trim());
      if (!Number.isNaN(parsed) && inputEl.value.trim() !== '') {
        edge.weight = parsed;
        const graphData = getContainerGraphData(containerEl);
        syncGraphDataToContainer(containerEl, graphData);
        requestRender();
      }
      modal.close();
    };
    if (saveBtn) saveBtn.onclick = commitWeight;
    if (inputEl) {
      inputEl.addEventListener('keydown', (ev) => {
        if (ev.key === 'Enter') commitWeight();
      });
    }
  };

  const openEdgeContextMenu = (edge) => {
    const modal = getGraphModal();
    if (!modal) return;
    const uLabel = edge.source.label ?? edge.source.id;
    const vLabel = edge.target.label ?? edge.target.id;
    setModalTitle(modal, `Edge Options (${uLabel} - ${vLabel})`);
    modal.setContent(`
      <button type="button" id="fw-graph-edge-del" class="vscode-btn-secondary" style="width: 100%; color: #f87777;">Delete Edge</button>
    `);
    modal.open();

    const delBtn = modal.body.querySelector('#fw-graph-edge-del');
    if (delBtn) {
      delBtn.onclick = () => {
        const graphData = getContainerGraphData(containerEl);
        const idx = graphData.edges.indexOf(edge);
        if (idx !== -1) graphData.edges.splice(idx, 1);
        if (containerEl._hoveredEdge === edge) containerEl._hoveredEdge = null;
        syncGraphDataToContainer(containerEl, graphData);
        requestRender();
        modal.close();
      };
    }
  };

  const openNodeContextMenu = (node) => {
    const modal = getGraphModal();
    if (!modal) return;
    const currentDisplay = node.label !== undefined ? node.label : node.id;
    const safeDisplay = String(currentDisplay).replace(/"/g, '&quot;');
    setModalTitle(modal, `Node Options (ID: ${node.id})`);
    modal.setContent(`
      <div style="display: flex; flex-direction: column; gap: 0.5rem;">
        <label style="font-size: 0.85rem; color: var(--text-muted);">Node Value (Internal ID: ${node.id})</label>
        <div style="display: flex; align-items: stretch; gap: 0.4rem;">
          <input type="text" id="fw-graph-node-val-input" class="param-input-field" style="flex: 1; height: var(--control-btn-height-desktop); min-height: var(--control-btn-height-desktop);" value="${safeDisplay}" placeholder="Node display value" />
          <button type="button" id="fw-graph-node-val-save" class="vscode-btn-secondary" style="height: var(--control-btn-height-desktop); min-height: var(--control-btn-height-desktop); padding: 0 0.75rem;">Update</button>
        </div>
        <hr style="border: none; border-top: 1px solid var(--border-color); margin: 0.25rem 0;" />
        <button type="button" id="fw-graph-node-del" class="vscode-btn-secondary" style="width: 100%; color: #f87777;">Delete Node</button>
      </div>
    `);
    modal.open();

    const inputEl = modal.body.querySelector('#fw-graph-node-val-input');
    const saveBtn = modal.body.querySelector('#fw-graph-node-val-save');
    const delBtn = modal.body.querySelector('#fw-graph-node-del');

    if (inputEl) {
      requestAnimationFrame(() => { inputEl.focus(); inputEl.select(); });
    }

    const commitNodeValue = () => {
      const nextVal = inputEl.value.trim();
      if (nextVal !== '') {
        node.label = nextVal;
        requestRender();
      }
      modal.close();
    };

    if (saveBtn) saveBtn.onclick = commitNodeValue;
    if (inputEl) {
      inputEl.addEventListener('keydown', (ev) => {
        if (ev.key === 'Enter') commitNodeValue();
      });
    }

    if (delBtn) {
      delBtn.onclick = () => {
        const graphData = getContainerGraphData(containerEl);
        graphData.nodes = graphData.nodes.filter(n => n !== node);
        graphData.edges = graphData.edges.filter(e => e.source !== node && e.target !== node);
        syncGraphDataToContainer(containerEl, graphData);
        requestRender();
        modal.close();
      };
    }
  };

  const openCanvasContextMenu = (worldPt) => {
    const modal = getGraphModal();
    if (!modal) return;
    const graphData = getContainerGraphData(containerEl);
    const suggestedName = generateDefaultNodeLabel(graphData.nodes);
    const safeSuggested = String(suggestedName).replace(/"/g, '&quot;');

    setModalTitle(modal, 'Canvas Options');
    modal.setContent(`
      <div style="display: flex; flex-direction: column; gap: 0.45rem;">
        <label style="font-size: 0.85rem; color: var(--text-muted);">Add Node</label>
        <div style="display: flex; align-items: stretch; gap: 0.4rem; margin-bottom: 0.25rem;">
          <input type="text" id="fw-graph-add-node-input" class="param-input-field" style="flex: 1; height: var(--control-btn-height-desktop); min-height: var(--control-btn-height-desktop);" placeholder="Name (default: ${safeSuggested})" />
          <button type="button" id="fw-graph-add-node-btn" class="vscode-btn-secondary" style="height: var(--control-btn-height-desktop); min-height: var(--control-btn-height-desktop); padding: 0 0.75rem;">Add node</button>
        </div>
        <hr style="border: none; border-top: 1px solid var(--border-color); margin: 0.15rem 0;" />
        <button type="button" id="fw-rearrange-nodes" class="vscode-btn-secondary" style="width: 100%;">Rearrange nodes</button>
        <button type="button" id="fw-copy-edge-list" class="vscode-btn-secondary" style="width: 100%;">Copy as edge list</button>
        <button type="button" id="fw-copy-adj-list" class="vscode-btn-secondary" style="width: 100%;">Copy as adjacency list</button>
        <button type="button" id="fw-copy-adj-matrix" class="vscode-btn-secondary" style="width: 100%;">Copy as adjacency matrix</button>
        <button type="button" id="fw-copy-json-attr" class="vscode-btn-secondary" style="width: 100%;">Copy as JSON (preserves attributes)</button>
      </div>
    `);
    modal.open();

    const addInput = modal.body.querySelector('#fw-graph-add-node-input');
    const addBtn = modal.body.querySelector('#fw-graph-add-node-btn');

    if (addInput) {
      requestAnimationFrame(() => addInput.focus());
    }

    const handleAddNode = () => {
      const rawVal = addInput ? addInput.value.trim() : '';
      const finalLabel = rawVal !== '' ? rawVal : generateDefaultNodeLabel(graphData.nodes);
      const newId = allocateNextNodeId(graphData);
      graphData.nodes.push({
        id: newId,
        label: finalLabel,
        x: worldPt.x,
        y: worldPt.y
      });
      syncGraphDataToContainer(containerEl, graphData);
      requestRender();
      modal.close();
    };

    if (addBtn) addBtn.onclick = handleAddNode;
    if (addInput) {
      addInput.addEventListener('keydown', (ev) => {
        if (ev.key === 'Enter') handleAddNode();
      });
    }

    // --- Rearrange Nodes Handler ---
    const rearrangeBtn = modal.body.querySelector('#fw-rearrange-nodes');
    if (rearrangeBtn) {
      rearrangeBtn.onclick = () => {
        const w = (canvas && canvas.clientWidth) ? canvas.clientWidth : 800;
        const h = (canvas && canvas.clientHeight) ? canvas.clientHeight : 600;

        // Re-execute simulated annealing crossing minimization & circular placement
        applyCircularNodeLayout(graphData.nodes, w, h, graphData.edges);

        // Recalculate edge geometries and bounds
        refreshEdgeFlags(graphData);
        syncGraphDataToContainer(containerEl, graphData);
        requestRender();

        // Automatically zoom/center the camera to fit the rearranged graph
        const activeContainerObj = (typeof dsContainers !== 'undefined')
          ? dsContainers.find(c => c.element === containerEl)
          : null;
        if (activeContainerObj && typeof activeContainerObj.centerView === 'function') {
          activeContainerObj.centerView();
        }

        modal.close();
      };
    }

    const copyAndClose = (text) => {
      navigator.clipboard?.writeText(text).catch(() => { });
      modal.close();
    };

    modal.body.querySelector('#fw-copy-edge-list').onclick = () => copyAndClose(formatGraphAsEdgeList(graphData));
    modal.body.querySelector('#fw-copy-adj-list').onclick = () => copyAndClose(formatGraphAsAdjacencyList(graphData));
    modal.body.querySelector('#fw-copy-adj-matrix').onclick = () => copyAndClose(formatGraphAsAdjacencyMatrix(graphData));
    modal.body.querySelector('#fw-copy-json-attr').onclick = () => copyAndClose(formatGraphAsJsonWithAttributes(graphData));
  };

  // Track last node pointerdown for double-click drag edge creation
  let lastNodeDown = { time: 0, node: null };

  // 1. Left-Click: Weight Pill -> Edit Weight | Double-Click Drag Node -> Create Edge | Single-Click Drag Node -> Move Node
  canvas.addEventListener('pointerdown', (e) => {
    if (e.pointerType === 'mouse' && (e.button !== 0 || e.shiftKey)) return;

    // Allow clicking selectable candidate nodes or edges during Manual Simulation Mode
    if (window.isSimulating) {
      const inter = containerEl._simStep?.interaction;
      if (inter && Array.isArray(inter.candidateNodeIds)) {
        const graphData = getContainerGraphData(containerEl);
        const worldPt = screenToWorld(e.clientX, e.clientY);
        const clickedNode = hitTestNode(worldPt.x, worldPt.y);
        if (clickedNode && inter.candidateNodeIds.map(String).includes(String(clickedNode.id))) {
          e.stopImmediatePropagation();
          e.preventDefault();
          containerEl._hoveredEdge = null;
          canvas.style.cursor = '';
          if (typeof window.submitManualSimChoice === 'function') {
            window.submitManualSimChoice(String(clickedNode.id));
          }
          return;
        }

        const clickedEdge = hitTestWeightBox(worldPt.x, worldPt.y) || hitTestEdge(worldPt.x, worldPt.y);
        if (clickedEdge) {
          const sId = String(typeof clickedEdge.source === 'object' ? clickedEdge.source.id : clickedEdge.source);
          const tId = String(typeof clickedEdge.target === 'object' ? clickedEdge.target.id : clickedEdge.target);
          const srcId = String(inter.sourceNodeId);
          const candSet = inter.candidateNodeIds.map(String);

          let chosenId = null;
          if (sId === srcId && candSet.includes(tId)) {
            chosenId = tId;
          } else if (!graphData.isDirected && tId === srcId && candSet.includes(sId)) {
            chosenId = sId;
          }

          if (chosenId && typeof window.submitManualSimChoice === 'function') {
            e.stopImmediatePropagation();
            e.preventDefault();
            containerEl._hoveredEdge = null;
            canvas.style.cursor = '';
            window.submitManualSimChoice(chosenId);
          }
        }
      }
      return;
    }

    const worldPt = screenToWorld(e.clientX, e.clientY);

    // Check weight box first
    const hitWeightEdge = hitTestWeightBox(worldPt.x, worldPt.y);
    if (hitWeightEdge) {
      e.stopImmediatePropagation();
      e.preventDefault();
      openEditWeightModal(hitWeightEdge);
      return;
    }

    const hitNode = hitTestNode(worldPt.x, worldPt.y);
    if (!hitNode) return;

    e.stopImmediatePropagation();
    try { canvas.setPointerCapture(e.pointerId); } catch { }

    const now = performance.now();
    const isDoubleClickOnSameNode = (lastNodeDown.node === hitNode) && (now - lastNodeDown.time < 350);

    if (isDoubleClickOnSameNode) {
      lastNodeDown = { time: 0, node: null };
      containerEl._edgeCreateState = {
        pointerId: e.pointerId,
        sourceNode: hitNode,
        currX: worldPt.x,
        currY: worldPt.y,
        hoverTargetNode: hitNode
      };
      containerEl._hoveredEdge = null;
      canvas.style.cursor = 'crosshair';
      requestRender();
      return;
    }

    lastNodeDown = { time: now, node: hitNode };

    containerEl._dragState = {
      pointerId: e.pointerId,
      node: hitNode,
      offsetX: hitNode.x - worldPt.x,
      offsetY: hitNode.y - worldPt.y
    };
    containerEl._hoveredEdge = null;
    canvas.style.cursor = 'grabbing';
    requestRender();
  }, { capture: true });

  // 2. Pointer Move: Edge Creation Preview | Node Drag | Hover States
  canvas.addEventListener('pointermove', (e) => {
    const worldPt = screenToWorld(e.clientX, e.clientY);

    const edgeCreateState = containerEl._edgeCreateState;
    if (edgeCreateState && edgeCreateState.pointerId === e.pointerId) {
      e.stopImmediatePropagation();
      edgeCreateState.currX = worldPt.x;
      edgeCreateState.currY = worldPt.y;
      edgeCreateState.hoverTargetNode = hitTestNode(worldPt.x, worldPt.y);
      canvas.style.cursor = 'crosshair';
      requestRender();
      return;
    }

    const dragState = containerEl._dragState;
    if (dragState && dragState.pointerId === e.pointerId) {
      e.stopImmediatePropagation();
      dragState.node.x = worldPt.x + dragState.offsetX;
      dragState.node.y = worldPt.y + dragState.offsetY;
      canvas.style.cursor = 'grabbing';
      requestRender();
      return;
    }

    if (window.isSimulating) {
      const inter = containerEl._simStep?.interaction;
      if (inter && Array.isArray(inter.candidateNodeIds)) {
        const graphData = getContainerGraphData(containerEl);
        const candSet = inter.candidateNodeIds.map(String);
        const hitNode = hitTestNode(worldPt.x, worldPt.y);
        const isCandNode = hitNode && candSet.includes(String(hitNode.id));
        const hitEdge = hitTestWeightBox(worldPt.x, worldPt.y) || hitTestEdge(worldPt.x, worldPt.y);
        let isCandEdge = false;
        if (hitEdge) {
          const sId = String(typeof hitEdge.source === 'object' ? hitEdge.source.id : hitEdge.source);
          const tId = String(typeof hitEdge.target === 'object' ? hitEdge.target.id : hitEdge.target);
          const srcId = String(inter.sourceNodeId);
          isCandEdge =
            (sId === srcId && candSet.includes(tId)) ||
            (!graphData.isDirected && tId === srcId && candSet.includes(sId));
        }
        if (containerEl._hoveredEdge !== (isCandEdge ? hitEdge : null)) {
          containerEl._hoveredEdge = isCandEdge ? hitEdge : null;
          requestRender();
        }
        canvas.style.cursor = (isCandNode || isCandEdge) ? 'pointer' : '';
      } else {
        if (containerEl._hoveredEdge) {
          containerEl._hoveredEdge = null;
          requestRender();
        }
        canvas.style.cursor = '';
      }
      return;
    }

    const hitWeightEdge = hitTestWeightBox(worldPt.x, worldPt.y);
    if (hitWeightEdge) {
      if (containerEl._hoveredEdge !== hitWeightEdge) {
        containerEl._hoveredEdge = hitWeightEdge;
        requestRender();
      }
      canvas.style.cursor = 'text';
      return;
    }

    const hitNode = hitTestNode(worldPt.x, worldPt.y);
    if (hitNode) {
      if (containerEl._hoveredEdge) {
        containerEl._hoveredEdge = null;
        requestRender();
      }
      canvas.style.cursor = 'grab';
      return;
    }

    const hitEdge = hitTestEdge(worldPt.x, worldPt.y);
    if (hitEdge !== containerEl._hoveredEdge) {
      containerEl._hoveredEdge = hitEdge;
      requestRender();
    }
    canvas.style.cursor = '';
  }, { capture: true });

  const endPointerInteraction = (e) => {
    const edgeCreateState = containerEl._edgeCreateState;
    if (edgeCreateState && edgeCreateState.pointerId === e.pointerId) {
      e.stopImmediatePropagation();
      try { canvas.releasePointerCapture(e.pointerId); } catch { }
      const worldPt = screenToWorld(e.clientX, e.clientY);
      const targetNode = e.type !== 'pointercancel' ? hitTestNode(worldPt.x, worldPt.y) : null;
      const sourceNode = edgeCreateState.sourceNode;
      containerEl._edgeCreateState = null;

      if (targetNode && sourceNode) {
        const graphData = getContainerGraphData(containerEl);
        const alreadyExists = graphData.edges.some(edge => {
          const sameDir = edge.source === sourceNode && edge.target === targetNode;
          const oppDir = !graphData.isDirected && edge.source === targetNode && edge.target === sourceNode;
          return sameDir || oppDir;
        });

        if (!alreadyExists) {
          graphData.edges.push({
            source: sourceNode,
            target: targetNode,
            weight: 1 // Defaults to 1 when created
          });
          syncGraphDataToContainer(containerEl, graphData);
        }
      }
      canvas.style.cursor = targetNode ? 'grab' : '';
      requestRender();
      return;
    }

    const dragState = containerEl._dragState;
    if (!dragState || dragState.pointerId !== e.pointerId) return;
    e.stopImmediatePropagation();
    try { canvas.releasePointerCapture(e.pointerId); } catch { }
    containerEl._dragState = null;
    canvas.style.cursor = 'grab';
    requestRender();
  };

  canvas.addEventListener('pointerup', endPointerInteraction, { capture: true });
  canvas.addEventListener('pointercancel', endPointerInteraction, { capture: true });

  canvas.addEventListener('pointerleave', () => {
    if (containerEl._hoveredEdge) {
      containerEl._hoveredEdge = null;
      requestRender();
    }
  });

  // 3. Right-Click Context Menu: Node Menu | Edge Menu | Canvas Menu
  canvas.addEventListener('contextmenu', (e) => {
    if (window.isSimulating) {
      e.preventDefault();
      e.stopPropagation();
      if (typeof window.showSimulationRunningWarning === 'function') {
        window.showSimulationRunningWarning();
      }
      return;
    }
    e.preventDefault();
    e.stopPropagation();

    const worldPt = screenToWorld(e.clientX, e.clientY);
    const hitNode = hitTestNode(worldPt.x, worldPt.y);
    if (hitNode) {
      openNodeContextMenu(hitNode);
      return;
    }

    const hitEdge = hitTestWeightBox(worldPt.x, worldPt.y) || hitTestEdge(worldPt.x, worldPt.y);
    if (hitEdge) {
      openEdgeContextMenu(hitEdge);
      return;
    }

    openCanvasContextMenu(worldPt);
  });
}

// Standardized Dynamic Module Exports
export {
  drawGraph as draw,
  setupGraphInteractions as setupInteractions,
  getContainerGraphData as getData
};

export const practiceConfig = {
  dsCategory: 'graph',
  funcName: 'my_graph_algorithm',
  template: `def my_graph_algorithm(graph, *args, **kwargs):\n    # Write your custom graph algorithm here.\n    # Only operations on 'graph' inside my_graph_algorithm are visualized.\n    for u in graph:\n        for v in graph[u]:\n            pass\n    return None\n`,

  extractDsPayload(containerEl) {
    const graphData = getContainerGraphData(containerEl);
    const { nodes, edges, isDirected, isWeighted } = graphData;
    const adj = {};

    nodes.forEach((n) => {
      adj[String(n.id)] = [];
    });

    edges.forEach((e) => {
      const uId = String(typeof e.source === 'object' ? e.source.id : e.source);
      const vId = String(typeof e.target === 'object' ? e.target.id : e.target);
      const w = e.weight ?? 1;

      if (adj[uId]) {
        adj[uId].push(isWeighted ? [vId, w] : vId);
      }
      if (!isDirected && uId !== vId && adj[vId]) {
        adj[vId].push(isWeighted ? [uId, w] : uId);
      }
    });

    return adj;
  },

  extractNodeLabels(containerEl) {
    const graphData = getContainerGraphData(containerEl);
    const labels = {};
    (graphData.nodes || []).forEach((n) => {
      labels[String(n.id)] = String(n.label ?? n.id);
    });
    return labels;
  },

  buildSteps(pyFrames, error) {
    const steps = [];
    const fullExplanationLines = [];

    pyFrames.forEach((frame, idx) => {
      const pyLine = frame.line;
      const sv = frame.stateVars || {};
      const vis = frame.visual || {};

      const stepDescription =
        frame.event === 'return'
          ? `Function returned ${sv.return}`
          : `Executing line ${pyLine}`;

      fullExplanationLines.push(`Step ${idx + 1}: ${stepDescription}`);

      steps.push({
        lines: { Python: { active: String(pyLine) } },
        activeLineKey: 'active',
        activeIndex: vis.activeIndex ?? -1,
        foundIndex: vis.foundIndex ?? -1,
        checkedIndices: vis.checkedIndices || [],
        activeNodeId: vis.activeNodeId ?? null,
        activeNodeIds: vis.activeNodeIds || [],
        foundNodeId: vis.foundNodeId ?? null,
        visitedNodes: vis.visitedNodes || [],
        activeEdge: vis.activeEdge || null,
        visitedEdges: vis.visitedEdges || [],
        interaction: frame.interaction || null,
        stateVars: sv,
        stepDescription,
      });
    });

    if (error) {
      const errLine = error.line || (pyFrames.length ? pyFrames[pyFrames.length - 1].line : 1);
      const lastStep = steps[steps.length - 1];
      const errDesc = `${error.type}: ${error.message}`;
      fullExplanationLines.push(`Error (Line ${errLine}): ${errDesc}`);

      steps.push({
        ...(lastStep || {}),
        lines: { Python: { active: String(errLine) } },
        activeLineKey: 'active',
        stateVars: {
          ...(lastStep ? lastStep.stateVars : {}),
          error: errDesc,
        },
        stepDescription: errDesc,
        isError: true,
      });
    }

    return { steps, fullExplanationLines, error };
  },
};