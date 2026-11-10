export function generateRandomInput(settings = {}, extraInputs = {}) {
  const vCount = Math.max(2, Math.min(26, parseInt(settings['Vertex Count'], 10) || 6));
  const isFullyConnected = Boolean(settings['Fully Connected']);
  const isSparse = Boolean(settings['Sparse']);
  const isBipartite = Boolean(settings['Bipartite']);

  // Read weight bounds
  let minWeight = parseInt(settings['Min Weight'], 10);
  let maxWeight = parseInt(settings['Max Weight'], 10);
  if (Number.isNaN(minWeight)) minWeight = -999;
  if (Number.isNaN(maxWeight)) maxWeight = 999;
  
  // Enforce bounds [-999, 999]
  minWeight = Math.max(-999, Math.min(999, minWeight));
  maxWeight = Math.max(-999, Math.min(999, maxWeight));
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
      }
    }
  } else {
    for (let i = 0; i < vCount; i++) {
      for (let j = i + 1; j < vCount; j++) {
        candidateEdges.push([vertices[i], vertices[j]]);
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

  // Shuffle candidate edges
  for (let i = candidateEdges.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [candidateEdges[i], candidateEdges[j]] = [candidateEdges[j], candidateEdges[i]];
  }

  const selected = candidateEdges.slice(0, targetEdges);
  
  // FORMAT AS EDGE LIST OF TUPLES WITH WEIGHTS
  const edgesStr = selected
    .map(([u, v]) => {
      const weight = Math.floor(Math.random() * (maxWeight - minWeight + 1)) + minWeight;
      return `(${u},${v},${weight})`;
    })
    .join(', ');
    
  return `[${edgesStr}]`;
}

export default generateRandomInput;