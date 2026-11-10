// data-structures/random/Graph.js
const DENSITY_KEYS = ['Fully Connected', 'Sparse'];

function computeMaxPossibleEdges(vCount, isBipartite, isDirected) {
  if (isBipartite) {
    const setA = Math.floor(vCount / 2);
    const setB = vCount - setA;
    return Math.max(1, setA * setB * (isDirected ? 2 : 1));
  }
  return Math.max(1, isDirected ? vCount * (vCount - 1) : Math.floor((vCount * (vCount - 1)) / 2));
}

export function onSettingsChange({ changedKey, settings, extraInputs, ui }) {
  // 1. Mutual exclusivity between Fully Connected and Sparse
  if (DENSITY_KEYS.includes(changedKey) && settings[changedKey]) {
    for (const key of DENSITY_KEYS) {
      if (key !== changedKey) {
        ui.setChecked(key, false);
        settings[key] = false;
      }
    }
  }

  // 2. Dynamically update Edge Count slider bounds based on Vertex Count, Bipartite, and Directed
  const vCount = Math.max(2, Math.min(26, parseInt(settings['Vertex Count'], 10) || 6));
  const isBipartite = Boolean(settings['Bipartite']);
  const isDirected = Boolean(extraInputs['Directed']);
  const maxPossibleEdges = computeMaxPossibleEdges(vCount, isBipartite, isDirected);

  ui.setRangeBounds('Edge Count', 1, maxPossibleEdges);

  const warnings = [];
  if (settings['Fully Connected']) {
    ui.setValue('Edge Count', maxPossibleEdges);
    warnings.push(`"Fully Connected" is enabled: Edge Count is locked to the maximum (${maxPossibleEdges}).`);
  } else if (settings['Sparse']) {
    const sparseTarget = Math.min(maxPossibleEdges, Math.max(vCount - 1, Math.floor(vCount * 1.25)));
    warnings.push(`"Sparse" is enabled: Generator will use ${sparseTarget} edges.`);
  }

  // 3. Check weight bounds
  const minW = parseInt(settings['Min Weight'], 10);
  const maxW = parseInt(settings['Max Weight'], 10);
  if (!Number.isNaN(minW) && !Number.isNaN(maxW) && minW > maxW) {
    warnings.push(`Min Weight (${minW}) is greater than Max Weight (${maxW}); they will be swapped automatically.`);
  }

  ui.setWarning(warnings);
}

export function generateRandomInput(settings = {}, extraInputs = {}) {
  const vCount = Math.max(2, Math.min(26, parseInt(settings['Vertex Count'], 10) || 6));
  const isFullyConnected = Boolean(settings['Fully Connected']);
  const isSparse = Boolean(settings['Sparse']);
  const isBipartite = Boolean(settings['Bipartite']);
  const isDirected = Boolean(extraInputs['Directed']);

  let minWeight = parseInt(settings['Min Weight'], 10);
  let maxWeight = parseInt(settings['Max Weight'], 10);
  if (Number.isNaN(minWeight)) minWeight = 1;
  if (Number.isNaN(maxWeight)) maxWeight = 20;

  minWeight = Math.max(-999, Math.min(999, Math.trunc(minWeight)));
  maxWeight = Math.max(-999, Math.min(999, Math.trunc(maxWeight)));
  if (minWeight > maxWeight) {
    [minWeight, maxWeight] = [maxWeight, minWeight];
  }

  const vertices = Array.from({ length: vCount }, (_, i) => String.fromCharCode(65 + i));
  const candidateEdges = [];

  if (isBipartite) {
    const split = Math.max(1, Math.floor(vCount / 2));
    const setA = vertices.slice(0, split);
    const setB = vertices.slice(split);
    for (const u of setA) {
      for (const v of setB) {
        candidateEdges.push([u, v]);
        if (isDirected) candidateEdges.push([v, u]);
      }
    }
  } else {
    for (let i = 0; i < vCount; i++) {
      for (let j = i + 1; j < vCount; j++) {
        candidateEdges.push([vertices[i], vertices[j]]);
        if (isDirected) candidateEdges.push([vertices[j], vertices[i]]);
      }
    }
  }

  const maxPossible = candidateEdges.length;
  let targetEdges = parseInt(settings['Edge Count'], 10) || (vCount + 1);

  if (isFullyConnected) {
    targetEdges = maxPossible;
  } else if (isSparse) {
    targetEdges = Math.min(maxPossible, Math.max(vCount - 1, Math.floor(vCount * 1.25)));
  } else {
    targetEdges = Math.max(1, Math.min(maxPossible, targetEdges));
  }

  for (let i = candidateEdges.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [candidateEdges[i], candidateEdges[j]] = [candidateEdges[j], candidateEdges[i]];
  }

  const selected = candidateEdges.slice(0, targetEdges);
  const edgesStr = selected
    .map(([u, v]) => {
      const weight = Math.floor(Math.random() * (maxWeight - minWeight + 1)) + minWeight;
      return `(${u},${v},${weight})`;
    })
    .join(', ');

  return `[${edgesStr}]`;
}

export default generateRandomInput;