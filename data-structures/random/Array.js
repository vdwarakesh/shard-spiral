// data-structures/random/Array.js
export function generateRandomInput(settings = {}) {
    const length = Math.max(1, Math.min(26, parseInt(settings['Array Length'], 10) || 8));

    let minVal = parseInt(settings['Min Value'], 10);
    let maxVal = parseInt(settings['Max Value'], 10);
    if (Number.isNaN(minVal)) minVal = 1;
    if (Number.isNaN(maxVal)) maxVal = 50;

    // Enforce integer bounds [-999, 999]
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
        // Unique integers when range is wide enough
        const used = new Set();
        while (result.length < length) {
            const candidate = Math.floor(Math.random() * rangeSize) + minVal;
            if (!used.has(candidate)) {
                used.add(candidate);
                result.push(candidate);
            }
        }
    } else {
        // Allow duplicates (or fallback if range < length), ensuring at least one duplicate pair when possible
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

    // RETURN FORMATTED ARRAY
    return `[${result.join(', ')}]`;
}

export default generateRandomInput;