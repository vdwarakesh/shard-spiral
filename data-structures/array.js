// dsa/Array.js

import * as d3Module from './d3.js';
const d3 = window.d3 || d3Module;

// ========== Hyperparameters ==========
export const ARRAY_HYPERPARAMETERS = {
  // ----- Layout -----
  MIN_BAR_HEIGHT_RATIO: 0.10, // Least element is 10% of the canvas height
  MAX_BAR_HEIGHT_RATIO: 0.30, // Max element is 30% of the canvas height (reaches 30% limit from 60% baseline)
  MIN_BAR_HEIGHT: 100,         // Absolute floor on bar height in world px, regardless of ratio
  MAX_BAR_HEIGHT: 480,        // Absolute ceiling on bar height in world px, regardless of ratio
  MIN_HEIGHT_SPREAD: 160,      // Minimum gap enforced between the shortest and tallest bar, so scaling never collapses
  TOP_LIMIT_RATIO: 0.30,      // Top of the tallest bar sits at 30% from the top of the canvas
  BOTTOM_BASELINE_RATIO: 0.60,// Baseline of all bars sits at 60% from the top of the canvas
  HORIZONTAL_SPAN_RATIO: 0.70,// Array spans up to 70% of the canvas width
  MAX_BAR_WIDTH: 50,          // Maximum width of a single bar in world px
  MIN_BAR_WIDTH: 50,          // Minimum width of a single bar in world px
  BAR_PADDING: 0.22,          // Padding ratio between bars (for d3.scaleBand)
  FONT_FAMILY: "'Adwaita Sans', -apple-system, BlinkMacSystemFont, sans-serif",

  // ----- Fonts -----
  VALUE_FONT_SIZE: 20,
  INDEX_FONT_SIZE: 20,
  VALUE_LABEL_OFFSET: 20,     // distance above baseline for the value label
  INDEX_LABEL_OFFSET: 20,     // distance below baseline for the index label

  // ----- Colors: CSS variable names (guaranteed to exist on :root) -----
  BAR_FILL_VAR: '--ds-primary',
  TEXT_BRIGHT_VAR: '--text-bright',
  TEXT_DARK_VAR: '--text-dark',

  // Simulation state: "found" bar (e.g. binary/linear search target located)
  FOUND_FILL_VAR: '--ds-found-fill',

  // Simulation state: "current" bar being inspected
  CURRENT_FILL_VAR: '--ds-current-fill',

  // Simulation state: bar already checked and ruled out (uses its own fill color, dimmed)
  CHECKED_COLOR_VAR: '--ds-checked-primary',

  // Opaque default alpha for normal bars
  DEFAULT_ALPHA: 1,
};

/**
 * Resolves every *_VAR entry in the hyperparameters object into a flat set of
 * concrete style values, reading each CSS custom property from :root via
 * getComputedStyle. These variables are guaranteed to be defined, so no fallback
 * values are applied.
 */
function resolveStyleHyperparameters(hp) {
  const rootStyle = getComputedStyle(document.documentElement);
  const resolved = { ...hp };

  const readVar = (varName) => rootStyle.getPropertyValue(varName).trim();

  resolved.BAR_FILL = readVar(hp.BAR_FILL_VAR);
  resolved.TEXT_BRIGHT = readVar(hp.TEXT_BRIGHT_VAR);
  resolved.TEXT_DARK = readVar(hp.TEXT_DARK_VAR);

  resolved.FOUND_FILL = readVar(hp.FOUND_FILL_VAR);
  resolved.CURRENT_FILL = readVar(hp.CURRENT_FILL_VAR);
  resolved.CHECKED_COLOR = readVar(hp.CHECKED_COLOR_VAR);

  return resolved;
}

function recomputeNumericMagnitudes(items) {
  const allNumbers = items.length > 0 && items.every((d) => d.isNumber);
  items.forEach((d, idx) => {
    if (allNumbers || d.isNumber) {
      d.numericValue = Number(d.value);
    } else {
      const strVal = String(d.value);
      d.numericValue = strVal.length + (strVal.charCodeAt(0) || 0) / 255;
    }
    d.index = idx;
  });
  return items;
}

export function parseSingleToken(rawVal) {
  const trimmed = String(rawVal ?? '').trim();
  const num = Number(trimmed);
  const isNumber = trimmed !== '' && !Number.isNaN(num) && Number.isFinite(num);
  return {
    raw: trimmed,
    value: isNumber ? num : trimmed,
    isNumber,
  };
}

/**
 * Parses flexible array input formats:
 * - Space-separated: "1 2 3"
 * - Comma-separated: "1,2,3"
 * - Bracketed or mixed: "[1, 2, 3]", "(1 2 3)", "{1,2,3 1 2 3"
 * - Strings & quoted tokens: "apple, banana, 'cherry pie'"
 */
export function parseArrayInput(rawInput) {
  if (rawInput === null || rawInput === undefined) return [];
  let str = String(rawInput).trim();
  if (!str) return [];

  str = str.replace(/^[\[\(\{\s]+|[\]\)\}\s]+$/g, '').trim();
  if (!str) return [];

  const tokenRegex = /"([^"]*)"|'([^']*)'|([^,\s\[\]\(\)\{\}]+)/g;
  const items = [];
  let match;

  while ((match = tokenRegex.exec(str)) !== null) {
    const quoted = match[1] !== undefined ? match[1] : match[2];
    const unquoted = match[3];
    const rawToken = quoted !== undefined ? quoted : unquoted;

    if (quoted !== undefined) {
      items.push({ raw: rawToken, value: rawToken, isNumber: false });
    } else {
      items.push(parseSingleToken(rawToken));
    }
  }

  return recomputeNumericMagnitudes(items);
}

function syncArrayDataToContainer(containerEl, items) {
  recomputeNumericMagnitudes(items);
  containerEl._arrayData = items;
  const serialized = items.map((d) => d.raw).join(', ');
  containerEl.userInput = serialized;
  containerEl.setAttribute('userInput', serialized);

  if (typeof window.updateDsHeaderWarningState === 'function') {
    window.updateDsHeaderWarningState();
  }

  // Instantly recompute metrics whenever the array is modified
  if (typeof window.updateMetadataUI === 'function') {
    window.updateMetadataUI();
  }
}

export function getContainerArrayData(containerEl) {
  if (!containerEl._arrayData) {
    const rawInput = containerEl.userInput ?? containerEl.getAttribute('userInput') ?? '';
    containerEl._arrayData = parseArrayInput(rawInput);
  }
  return containerEl._arrayData;
}

/**
 * Draws the array onto the canvas inside `containerEl` using D3 scales.
 */
export function drawArray(containerEl, camera = null, customHyperparams = {}) {
  if (!containerEl) return;

  const mergedHp = { ...ARRAY_HYPERPARAMETERS, ...customHyperparams };
  const hp = resolveStyleHyperparameters(mergedHp);

  const canvas = containerEl.querySelector('canvas.ds-grid-canvas') || containerEl.querySelector('canvas');
  if (!canvas) return;

  const data = getContainerArrayData(containerEl);
  containerEl._barHitBoxes = [];
  if (data.length === 0) return;

  const rect = canvas.getBoundingClientRect();
  const w = rect.width;
  const h = rect.height;
  if (w <= 0 || h <= 0) return;

  const dpr = Math.min(2, window.devicePixelRatio || 1);
  const ctx = canvas.getContext('2d');

  const cam = camera || containerEl._camera || { x: 0, y: 0, z: 1 };
  const useWorldOrigin = Boolean(camera || containerEl._camera);

  if (!containerEl._baseViewport || containerEl._baseViewport.w === 0) {
    containerEl._baseViewport = { w, h };
    containerEl._worldOrigin = {
      x: (w / (2 * cam.z)) - cam.x,
      y: (h / (2 * cam.z)) - cam.y,
    };
  }
  const baseW = useWorldOrigin ? containerEl._baseViewport.w : w;
  const baseH = useWorldOrigin ? containerEl._baseViewport.h : h;
  const originX = useWorldOrigin && containerEl._worldOrigin ? containerEl._worldOrigin.x : 0;
  const originY = useWorldOrigin && containerEl._worldOrigin ? containerEl._worldOrigin.y : 0;

  // Ratio-based sizing, clamped to the absolute MIN_BAR_HEIGHT / MAX_BAR_HEIGHT bounds.
  const minBarH = Math.min(Math.max(baseH * hp.MIN_BAR_HEIGHT_RATIO, hp.MIN_BAR_HEIGHT), hp.MAX_BAR_HEIGHT);
  const ratioMaxBarH = Math.min(Math.max(baseH * hp.MAX_BAR_HEIGHT_RATIO, hp.MIN_BAR_HEIGHT), hp.MAX_BAR_HEIGHT);
  let maxBarH = Math.max(ratioMaxBarH, minBarH + hp.MIN_HEIGHT_SPREAD);
  const baselineY = useWorldOrigin
    ? originY - (baseH / 2) + (baseH * hp.BOTTOM_BASELINE_RATIO)
    : (baseH * hp.BOTTOM_BASELINE_RATIO);

  // 1. Extract and sort unique numeric values
  const uniqueVals = [...new Set(data.map(d => d.numericValue))].sort((a, b) => a - b);
  const maxRank = uniqueVals.length - 1;
  const MIN_DELTA = 15;

  // 2. Ensure we have enough total vertical height for the strict minimum deltas
  if (maxBarH < minBarH + maxRank * MIN_DELTA) {
    maxBarH = minBarH + maxRank * MIN_DELTA;
  }

  const availableExtraSpace = Math.max(0, (maxBarH - minBarH) - (maxRank * MIN_DELTA));
  const totalValueSpan = maxRank > 0 ? (uniqueVals[maxRank] - uniqueVals[0]) : 1;

  // 3. Map values to heights: guarantee MIN_DELTA for every step, plus proportional extra space
  const heightMap = new Map();
  if (maxRank === 0) {
    heightMap.set(uniqueVals[0], maxBarH);
  } else {
    let currentHeight = minBarH;
    heightMap.set(uniqueVals[0], currentHeight);

    for (let i = 1; i <= maxRank; i++) {
      const valDiff = uniqueVals[i] - uniqueVals[i - 1];
      const linearShare = (valDiff / totalValueSpan) * availableExtraSpace;
      currentHeight += MIN_DELTA + linearShare;
      heightMap.set(uniqueVals[i], currentHeight);
    }
  }

  const maxSpanW = baseW * hp.HORIZONTAL_SPAN_RATIO;
  const idealTotalW = Math.min(maxSpanW, data.length * (hp.MAX_BAR_WIDTH / (1 - hp.BAR_PADDING)));
  const totalW = Math.max(idealTotalW, data.length * hp.MIN_BAR_WIDTH);

  const startX = useWorldOrigin ? (originX - totalW / 2) : ((baseW - totalW) / 2);
  const endX = startX + totalW;

  const xScale = d3.scaleBand()
    .domain(d3.range(data.length))
    .range([startX, endX])
    .paddingInner(hp.BAR_PADDING)
    .paddingOuter(hp.BAR_PADDING / 2);

  const barWidth = xScale.bandwidth();
  const stepX = xScale.step();

  containerEl._arrayLayoutMeta = { startX, stepX, barWidth, baselineY };

  ctx.save();
  if (useWorldOrigin) {
    ctx.setTransform(
      cam.z * dpr,
      0,
      0,
      cam.z * dpr,
      cam.x * cam.z * dpr,
      cam.y * cam.z * dpr
    );
  } else {
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }

  const dragState = containerEl._dragState;

  data.forEach((d, i) => {
    const isDraggingThis = dragState && dragState.index === i;
    const barH = heightMap.get(d.numericValue);
    const x = isDraggingThis ? (dragState.worldX - barWidth / 2) : xScale(i);
    const y = baselineY - barH;

    // Save world-space hitbox for right-click and drag hit-testing
    containerEl._barHitBoxes.push({
      index: i,
      x: xScale(i),
      y,
      w: barWidth,
      h: barH,
    });

    // Check if an algorithm simulation is currently highlighting this bar
    const simState = containerEl._simState;
    const isCurrentBar = simState && simState.activeIndex === i;
    const isFoundBar = simState && simState.foundIndex === i;
    const isCheckedBar = simState && Array.isArray(simState.checkedIndices) && simState.checkedIndices.includes(i);

    let currentFill = hp.BAR_FILL;
    let currentAlpha = hp.DEFAULT_ALPHA;

    if (isFoundBar) {
      currentFill = hp.FOUND_FILL;
      currentAlpha = hp.DEFAULT_ALPHA;
    } else if (isCurrentBar) {
      currentFill = hp.CURRENT_FILL;
      currentAlpha = hp.DEFAULT_ALPHA;
    } else if (isCheckedBar) {
      currentFill = hp.CHECKED_COLOR;
    }

    // 1. Sharp Rectangular Bar (no border-radius, no stroke)
    ctx.beginPath();
    ctx.rect(x, y, barWidth, barH);
    ctx.fillStyle = currentFill;
    ctx.globalAlpha = currentAlpha;
    ctx.fill();

    ctx.globalAlpha = hp.DEFAULT_ALPHA;

    // 2. Value Label (placed near the bottom inside the bar, right above the baseline)
    ctx.font = `700 ${hp.VALUE_FONT_SIZE}px ${hp.FONT_FAMILY}`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'bottom';
    const valX = x + barWidth / 2;
    const valY = baselineY - hp.VALUE_LABEL_OFFSET;

    ctx.fillStyle = hp.TEXT_DARK;
    ctx.fillText(String(d.value), valX, valY);

    // 3. Index Label (placed directly below the baseline, right below the value)
    ctx.font = `700 ${hp.INDEX_FONT_SIZE}px ${hp.FONT_FAMILY}`;
    ctx.fillStyle = hp.TEXT_BRIGHT;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'top';
    ctx.fillText(String(i), valX, baselineY + hp.INDEX_LABEL_OFFSET);
  });

  // Compute exact world-space bounding box of the entire array (tallest bar top to index label bottom)
  if (containerEl._barHitBoxes.length > 0) {
    let minX = Infinity;
    let minY = Infinity;
    let maxX = -Infinity;
    let maxY = -Infinity;

    for (const b of containerEl._barHitBoxes) {
      if (b.x < minX) minX = b.x;
      if (b.y < minY) minY = b.y;
      if (b.x + b.w > maxX) maxX = b.x + b.w;
      if (b.y + b.h > maxY) maxY = b.y + b.h;
    }

    // Include the index labels below the baseline in the vertical bounds
    const bottomWithLabels = maxY + hp.INDEX_LABEL_OFFSET + hp.INDEX_FONT_SIZE;
    containerEl._structureBounds = {
      minX,
      maxX,
      minY,
      maxY: bottomWithLabels,
    };
  } else {
    containerEl._structureBounds = null;
  }

  ctx.restore();
}

/**
 * Attaches right-click context menu (via FloatingWindow) and drag-to-reorder to an Array container.
 */
export function setupArrayInteractions(containerEl, requestRender) {
  const canvas = containerEl.querySelector('canvas');
  if (!canvas || containerEl._arrayInteractionsBound) return;
  containerEl._arrayInteractionsBound = true;

  let modal = null;
  const getModal = (title) => {
    if (!modal && window.FloatingWindow) {
      modal = new window.FloatingWindow(title);
    }
    if (modal) {
      const titleSpan = modal.overlay.querySelector('.modal-header span');
      if (titleSpan) titleSpan.textContent = title;
    }
    return modal;
  };

  const screenToWorld = (clientX, clientY) => {
    const r = canvas.getBoundingClientRect();
    const sx = clientX - r.left;
    const sy = clientY - r.top;
    const cam = containerEl._camera || { x: 0, y: 0, z: 1 };
    return {
      x: sx / cam.z - cam.x,
      y: sy / cam.z - cam.y,
    };
  };

  const hitTestBar = (wx, wy) => {
    const boxes = containerEl._barHitBoxes || [];
    for (let i = boxes.length - 1; i >= 0; i--) {
      const b = boxes[i];
      // Include the index label area just below the bar for easy clicking
      if (wx >= b.x && wx <= b.x + b.w && wy >= b.y && wy <= b.y + b.h + 26) {
        return b.index;
      }
    }
    return -1;
  };

  // Helper to open the second floating window for inputting values (with a Back button)
  const openValueInputModal = (title, placeholder, buttonText, onSubmit, onBack, initialValue = '') => {
    const win = getModal(title);
    if (!win) return;

    // Sanitize initial value for the HTML attribute
    const safeInitial = String(initialValue).replace(/"/g, '&quot;');

    win.setContent(`
      <div style="display: flex; flex-direction: column; gap: 0.5rem;">
        <input type="text" id="arr-fw-val" class="param-input-field" placeholder="${placeholder}" value="${safeInitial}" />
        <div style="display: flex; gap: 0.4rem;">
          <button type="button" id="arr-fw-back" class="vscode-btn-secondary" style="flex: 1;">Back</button>
          <button type="button" id="arr-fw-submit" class="vscode-btn-secondary" style="flex: 2;">${buttonText}</button>
        </div>
      </div>
    `);
    win.open();

    const inputEl = win.body.querySelector('#arr-fw-val');
    const handleConfirm = () => {
      const raw = inputEl.value.trim();
      if (!raw) return;
      onSubmit(raw);
      win.close();
      requestRender();
    };

    win.body.querySelector('#arr-fw-submit').onclick = handleConfirm;
    win.body.querySelector('#arr-fw-back').onclick = () => {
      if (onBack) onBack();
    };
    inputEl.addEventListener('keydown', (ev) => {
      if (ev.key === 'Enter') handleConfirm();
    });

    setTimeout(() => {
      inputEl.focus();
      if (initialValue) inputEl.select(); // Auto-highlight the existing value so typing immediately overwrites it
    }, 20);
  };

  // Step 1A: Options menu when right-clicking empty canvas space
  const openCanvasOptionsMenu = (data) => {
    const win = getModal('Array - Options');
    if (!win) return;

    win.setContent(`
      <div style="display: flex; flex-direction: column; gap: 0.5rem;">
        <button type="button" id="arr-opt-add" class="vscode-btn-secondary" style="width: 100%;">Add element</button>
        <button type="button" id="arr-opt-copy" class="vscode-btn-secondary" style="width: 100%;">Copy array values (CSV)</button>
      </div>
    `);
    win.open();

    win.body.querySelector('#arr-opt-add').onclick = () => {
      // Step 2: Settings window for "Add element"
      openValueInputModal(
        'Array - Add Element',
        'Enter value (or space/comma separated values)',
        'Add',
        (raw) => {
          const newTokens = parseArrayInput(raw);
          data.push(...newTokens);
          syncArrayDataToContainer(containerEl, data);
        },
        () => openCanvasOptionsMenu(data)
      );
    };

    win.body.querySelector('#arr-opt-copy').onclick = () => {
      const copyBtn = win.body.querySelector('#arr-opt-copy');
      // Map out the pure values and join them with a comma
      const csvStr = data.map(d => d.value).join(',');

      navigator.clipboard.writeText(csvStr).then(() => {
        copyBtn.textContent = 'Copied!';
        copyBtn.style.color = '#12a67c'; // Highlight green on success
        setTimeout(() => {
          win.close();
        }, 600);
      }).catch(err => {
        copyBtn.textContent = 'Failed to copy';
        copyBtn.style.color = '#ef4444'; // Red on fail
      });
    };
  };

  // Step 1B: Options menu when right-clicking an existing array element
  const openElementOptionsMenu = (data, hitIdx) => {
    const targetItem = data[hitIdx];
    const win = getModal(`Element [${hitIdx}] (${targetItem.value}) - Options`);
    if (!win) return;

    win.setContent(`
      <div style="display: flex; flex-direction: column; gap: 0.5rem;">
        <button type="button" id="arr-opt-edit" class="vscode-btn-secondary" style="width: 100%;">Edit element</button>
        <button type="button" id="arr-opt-left" class="vscode-btn-secondary" style="width: 100%;">Add to left</button>
        <button type="button" id="arr-opt-right" class="vscode-btn-secondary" style="width: 100%;">Add to right</button>
        <button type="button" id="arr-opt-del" class="vscode-btn-secondary" style="width: 100%; color: #ef4444;">Delete element</button>
      </div>
    `);
    win.open();

    win.body.querySelector('#arr-opt-edit').onclick = () => {
      openValueInputModal(
        `Element [${hitIdx}] - Edit`,
        'Enter new value',
        'Save',
        (raw) => {
          const newTokens = parseArrayInput(raw);
          // Splice out the 1 old element and insert the new one(s)
          data.splice(hitIdx, 1, ...newTokens);
          syncArrayDataToContainer(containerEl, data);
        },
        () => openElementOptionsMenu(data, hitIdx),
        targetItem.raw // Pre-fill the input with the current raw string
      );
    };

    win.body.querySelector('#arr-opt-left').onclick = () => {
      openValueInputModal(
        `Element [${hitIdx}] - Add to Left`,
        'Enter value (or space/comma separated values)',
        'Add to left',
        (raw) => {
          const newTokens = parseArrayInput(raw);
          data.splice(hitIdx, 0, ...newTokens);
          syncArrayDataToContainer(containerEl, data);
        },
        () => openElementOptionsMenu(data, hitIdx)
      );
    };

    win.body.querySelector('#arr-opt-right').onclick = () => {
      openValueInputModal(
        `Element [${hitIdx}] - Add to Right`,
        'Enter value (or space/comma separated values)',
        'Add to right',
        (raw) => {
          const newTokens = parseArrayInput(raw);
          data.splice(hitIdx + 1, 0, ...newTokens);
          syncArrayDataToContainer(containerEl, data);
        },
        () => openElementOptionsMenu(data, hitIdx)
      );
    };

    win.body.querySelector('#arr-opt-del').onclick = () => {
      data.splice(hitIdx, 1);
      syncArrayDataToContainer(containerEl, data);
      win.close();
      requestRender();
    };
  };

  // 1. Right-Click Context Menu Listener (Blocked during simulation + shows warning)
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
    const hitIdx = hitTestBar(worldPt.x, worldPt.y);
    const data = getContainerArrayData(containerEl);

    if (hitIdx === -1) {
      openCanvasOptionsMenu(data);
    } else {
      openElementOptionsMenu(data, hitIdx);
    }
  });

  // 2. Left-Click Drag on an Element -> Reorder Array (Silently disabled during simulation so camera pan/recenter works)
  canvas.addEventListener('pointerdown', (e) => {
    if (window.isSimulating) return;
    if (e.button !== 0 || e.shiftKey) return;

    const worldPt = screenToWorld(e.clientX, e.clientY);
    const hitIdx = hitTestBar(worldPt.x, worldPt.y);
    if (hitIdx === -1) return;

    // Stop camera double-click pan from hijacking bar dragging
    e.stopImmediatePropagation();
    try { canvas.setPointerCapture(e.pointerId); } catch { }

    containerEl._dragState = {
      pointerId: e.pointerId,
      index: hitIdx,
      worldX: worldPt.x,
    };
    canvas.style.cursor = 'grabbing';
    requestRender();
  }, { capture: true });

  canvas.addEventListener('pointermove', (e) => {
    const drag = containerEl._dragState;
    if (!drag || drag.pointerId !== e.pointerId) return;
    e.stopImmediatePropagation();

    const worldPt = screenToWorld(e.clientX, e.clientY);
    drag.worldX = worldPt.x;

    const data = getContainerArrayData(containerEl);
    const boxes = containerEl._barHitBoxes || [];
    if (boxes.length > 1) {
      // Find closest slot center to swap into
      let targetIdx = drag.index;
      for (let i = 0; i < boxes.length; i++) {
        const center = boxes[i].x + boxes[i].w / 2;
        if (i < drag.index && worldPt.x < center) {
          targetIdx = i;
          break;
        }
        if (i > drag.index && worldPt.x > center) {
          targetIdx = i;
        }
      }

      if (targetIdx !== drag.index) {
        const [moved] = data.splice(drag.index, 1);
        data.splice(targetIdx, 0, moved);
        drag.index = targetIdx;
        syncArrayDataToContainer(containerEl, data);
      }
    }

    requestRender();
  }, { capture: true });

  const endDrag = (e) => {
    const drag = containerEl._dragState;
    if (!drag || drag.pointerId !== e.pointerId) return;
    containerEl._dragState = null;
    canvas.style.cursor = '';
    requestRender();
  };

  canvas.addEventListener('pointerup', endDrag, { capture: true });
  canvas.addEventListener('pointercancel', endDrag, { capture: true });
}

export const practiceConfig = {
  dsCategory: 'sequence',
  funcName: 'my_array_algorithm',
  template: `def my_array_algorithm(arr, *args, **kwargs):\n    # Write your custom array algorithm here.\n    # Only operations on 'arr' inside my_array_algorithm are visualized.\n    for i in range(len(arr)):\n        val = arr[i]\n    return -1\n`,
  extractDsPayload(containerEl) {
    return getContainerArrayData(containerEl).map((d) => d.value);
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
        arrayValues: vis.arrayValues || null,
        stdout: frame.stdout || '',
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
        lines: { Python: { active: String(errLine) } },
        activeLineKey: 'active',
        stdout: lastStep ? (lastStep.stdout || '') : '',
        activeIndex: lastStep ? lastStep.activeIndex : -1,
        foundIndex: -1,
        checkedIndices: lastStep ? lastStep.checkedIndices : [],
        arrayValues: lastStep ? lastStep.arrayValues : null,
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

export {
  drawArray as draw,
  setupArrayInteractions as setupInteractions,
  getContainerArrayData as getData
};