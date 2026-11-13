// data-structures/random/Array.js
const SORT_KEYS = ['Sorted', 'Sorted (Desc)', 'Nearly Sorted'];

export function onSettingsChange({ changedKey, settings, ui }) {
  // 1. Enforce mutual exclusivity among sorting checkboxes
  if (SORT_KEYS.includes(changedKey) && settings[changedKey]) {
    for (const key of SORT_KEYS) {
      if (key !== changedKey) {
        ui.setChecked(key, false);
        settings[key] = false;
      }
    }
  }

  // 2. Check constraints and build warnings
  const warnings = [];
  const length = parseInt(settings['Array Length'], 10) || 1;
  let minV = parseInt(settings['Min Value'], 10);
  let maxV = parseInt(settings['Max Value'], 10);

  if (Number.isNaN(minV)) minV = 1;
  if (Number.isNaN(maxV)) maxV = 50;

  minV = Math.max(-999, Math.min(999, minV));
  maxV = Math.max(-999, Math.min(999, maxV));

  if (minV > maxV) {
    warnings.push(`Min Value (${minV}) is greater than Max Value (${maxV}); they will be swapped automatically.`);
  }

  const lo = Math.min(minV, maxV);
  const hi = Math.max(minV, maxV);
  const availableUnique = hi - lo + 1;

  if (!settings['Duplicates'] && length > availableUnique) {
    warnings.push(
      `Cannot avoid duplicates: Array Length (${length}) exceeds the number of unique integers (${availableUnique}) in [${lo}, ${hi}]. Duplicates will occur.`
    );
  }

  ui.setWarning(warnings);
}

export function generateRandomInput(settings = {}) {
  const length = Math.max(1, Math.min(26, parseInt(settings['Array Length'], 10) || 8));

  let minVal = parseInt(settings['Min Value'], 10);
  let maxVal = parseInt(settings['Max Value'], 10);
  if (Number.isNaN(minVal)) minVal = 1;
  if (Number.isNaN(maxVal)) maxVal = 50;

  minVal = Math.max(-999, Math.min(999, Math.trunc(minVal)));
  maxVal = Math.max(-999, Math.min(999, Math.trunc(maxVal)));
  if (minVal > maxVal) {
    [minVal, maxVal] = [maxVal, minVal];
  }

  const sortedAsc = Boolean(settings['Sorted']);
  const sortedDesc = Boolean(settings['Sorted (Desc)']);
  const nearlySorted = Boolean(settings['Nearly Sorted']);
  const allowDuplicates = settings['Duplicates'] !== undefined ? Boolean(settings['Duplicates']) : true;

  const rangeSize = maxVal - minVal + 1;
  const result = [];

  if (!allowDuplicates && rangeSize >= length) {
    const used = new Set();
    while (result.length < length) {
      const candidate = Math.floor(Math.random() * rangeSize) + minVal;
      if (!used.has(candidate)) {
        used.add(candidate);
        result.push(candidate);
      }
    }
  } else {
    for (let i = 0; i < length; i++) {
      result.push(Math.floor(Math.random() * rangeSize) + minVal);
    }
    if (allowDuplicates && length >= 2 && new Set(result).size === length) {
      const srcIdx = Math.floor(Math.random() * (length - 1));
      result[length - 1] = result[srcIdx];
    }
  }

  if (sortedAsc) {
    result.sort((a, b) => a - b);
  } else if (sortedDesc) {
    result.sort((a, b) => b - a);
  } else if (nearlySorted) {
    result.sort((a, b) => a - b);
    const swaps = Math.max(1, Math.floor(length / 5));
    for (let s = 0; s < swaps && length >= 2; s++) {
      const i = Math.floor(Math.random() * (length - 1));
      [result[i], result[i + 1]] = [result[i + 1], result[i]];
    }
  }

  return `[${result.join(', ')}]`;
}

export default generateRandomInput;