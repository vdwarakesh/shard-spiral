# Shard Spiral - Directory & Explorer Guide

This document explains how Shard Spiral reads its directory structure, how files are interpreted, how the Explorer filters work, and how to safely extend the library with new data structures and algorithms.

---

## 1. Directory Architecture

Shard Spiral splits its data structure and algorithm definitions into two primary folders to separate **user-facing content** from **executable source code**:

1. **`./dsa/` (User-Facing Explorer Tree):** 
   Contains the structural hierarchy, Python/C++/Java reference code, HTML notes, and algorithm tags. This is the exact folder structure mirrored in the app's left-hand Explorer panel.
2. **`./dsa-implementation/` (Executable Logic):** 
   Contains the JavaScript modules that physically draw the data structures on the canvas, evaluate constraints, define visual configurations (`description.json`), and process visualization steps.

---

## 2. How the `./dsa` Directory is Read

When the application loads (inside `loadDsaMetadata()`), it builds the Explorer tree dynamically without any hardcoded structural fallbacks. 

1. **Live Directory Auto-Indexing:** The app first attempts to fetch `./dsa/` directly via HTTP. If you are running a local development server (like `python -m http.server`), the server returns an auto-generated HTML directory listing. The app parses the `<a>` tags in this HTML to discover folders and files dynamically.
2. **JSON Manifest Fallback (`index.json`):** If the server blocks directory listing (which is standard for production), the app looks for `./dsa/index.json`. 

### Why is `index.json` strictly necessary in Production?
Standard web servers (Nginx, Apache) and static hosts (Vercel, Netlify, GitHub Pages) disable directory auto-indexing for security reasons. Fetching `./dsa/` on these platforms will return a `403 Forbidden` or a fallback `index.html`. 
To solve this, Shard Spiral requires a pre-generated JSON representation of the folder tree. 

**How to generate it:**
Whenever you add, rename, or delete files in the `./dsa/` folder, run the included python script from the root of your project:
```bash
python generate-tree.py
```
This instantly maps your actual file system into `./dsa/index.json` so the production frontend can read it.

---

## 3. Guaranteed Folders & Virtual Files

Not everything you see in the Explorer physically exists on the disk. To improve user experience, the app dynamically injects "Virtual" items during the tree-building phase:

* **`Configure & Generate`:** Injected at the top of every Data Structure folder. Clicking this loads that data structure's configuration parameters into the Settings card and opens its `Notes` file.
* **`My Files` (Root):** A virtual directory injected at the root level for users to create and upload unassociated local files.
* **`My <DS> Files` (Local):** A virtual directory injected into every Data Structure folder allowing users to store custom `.py` scripts or notes locally (persisted in IndexedDB up to a 5 MB quota).

---

## 4. How Filters Work

The Explorer includes a powerful filtering system (Favourites, Syllabus, Compatible, Language, Hide Notes) managed inside `renderMainAlgoTree()`.

* **Language Filter (`.py`, `.cpp`, `.java`):** Hides reference code files that do not match the selected extension.
* **Hide Notes Filter:** Hides `Notes`, `.html`, and `.txt` files from the built-in library (user-created HTML notes are exempt).
* **Favourites & Syllabus:** The app recursively scans folders. If a folder (like `Tree/Binary Tree`) does not match the active syllabus or favourites, but one of its child algorithms *does*, the parent folder remains visible so the user can navigate to the matching child.
* **Compatible Filter:** This is a *strict* filter. It only shows the Data Structure folder (and its `Algorithms/` subfolder) that exactly matches the currently active container on the canvas. All other sibling folders are hidden.
* **Algorithm Tags:** For algorithms, tags and constraints are read from `dsa/<DS>/Algorithms/<algorithm_name>.html`. The app fetches this file, reads everything before the first blank line (`\n\n`) or HTML tag (`<html`), and uses those key-value pairs (e.g., `sorted: true`) for both the Search bar and constraint validation.

---

## 5. Adding a New Data Structure

To add a new data structure (e.g., "Trie"), follow these steps:

1. **Create the User-Facing Folder:**
   Create `./dsa/Trie/`. Inside it, add a `Notes` file (no extension, containing HTML documentation) and optionally `trie.py`.
2. **Create the Implementation Folder:**
   Create `./dsa-implementation/data-structures/trie/`.
3. **Add `description.json`:**
   Inside the implementation folder, add `description.json`. Define your properties, placeholder text, extra inputs (checkboxes/text fields), and random generation parameters.
4. **Add the Canvas Logic (`trie.js`):**
   Create `trie.js` in the implementation folder. It must export a `draw(element, camera)` function and a `setupInteractions(element, renderFn)` function.
5. **Add the Random Logic (`random.js`):**
   If you defined random parameters in `description.json`, create `random.js` in the same folder. It must export a `default` or `generateRandomInput` function that returns the generated string.
6. **Update the Tree:**
   Run `python generate-tree.py`.

---

## 6. Adding a New Algorithm

To add a new algorithm (e.g., "Prefix Search") to an existing Data Structure (e.g., "Trie"):

1. **Create the User-Facing Files:**
   * Create `./dsa/Trie/Algorithms/prefix_search.py` (The readable reference code).
   * Create `./dsa/Trie/Algorithms/prefix_search.html`. 
2. **Define Tags and Constraints:**
   At the very top of `prefix_search.html`, add your tags and constraints, followed by a double newline, then your HTML notes:
   ```html
   search
   string-matching
   sorted: false

   <h3>Prefix Search Overview</h3>
   <p>This algorithm searches...</p>
   ```
3. **Add the Executable Logic:**
   Create `./dsa-implementation/algorithms/trie/prefix_search.js`. This file must export a `default` or `prefix_search` async function that takes `(containerElement, kwargs, context)` and returns an object containing `{ steps: [...], fullExplanationLines: [...] }`.
4. **Update the Tree:**
   Run `python generate-tree.py`.