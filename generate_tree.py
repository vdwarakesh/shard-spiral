import os
import json

def build_tree(path):
    name = os.path.basename(path)
    if os.path.isfile(path):
        return {"name": name, "type": "file"}
    
    children = []
    # Sort files and directories alphabetically
    for item in sorted(os.listdir(path)):
        # Ignore hidden files and the output json itself
        if not item.startswith('.') and item != 'index.json':
            children.append(build_tree(os.path.join(path, item)))
            
    return {"name": name, "type": "directory", "children": children}

if __name__ == '__main__':
    target_dir = './dsa'
    if os.path.exists(target_dir):
        tree = build_tree(target_dir)
        output_path = os.path.join(target_dir, 'index.json')
        with open(output_path, 'w') as f:
            json.dump(tree, f, indent=2)
        print(f"Successfully generated {output_path}")
    else:
        print(f"Directory {target_dir} not found.")