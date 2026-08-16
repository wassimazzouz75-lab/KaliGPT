#!/usr/bin/env python3
"""
find-skills.py — parcourir le dépôt et lister les fichiers Python pouvant contenir des "skills".
Usage:
  python find-skills.py --root . --filter agents/utils/tools
"""
import os
import argparse
import ast


def extract_info(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            src = f.read()
        tree = ast.parse(src)
        doc = ast.get_docstring(tree) or ""
        names = []
        for node in tree.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if getattr(target, "id", None) in ("SKILL_NAME", "NAME"):
                        if isinstance(node.value, ast.Constant):
                            names.append(node.value.value)
            if isinstance(node, ast.FunctionDef):
                for deco in node.decorator_list:
                    if getattr(deco, "id", None) in ("tool", "skill"):
                        names.append(node.name)
        return doc.strip().splitlines()[0] if doc else "", names
    except Exception:
        return "", []


def find_skills(root, exts=(".py",)):
    results = []
    for dirpath, _, files in os.walk(root):
        for fn in files:
            if not fn.endswith(exts):
                continue
            p = os.path.join(dirpath, fn)
            doc, names = extract_info(p)
            results.append({"path": p, "names": names, "doc": doc})
    return sorted(results, key=lambda x: x["path"]) 


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", "-r", default=".", help="Répertoire racine à scanner")
    parser.add_argument("--filter", "-f", help="Filtrer les chemins contenant cette sous-chaîne")
    args = parser.parse_args()

    items = find_skills(args.root)
    for it in items:
        if args.filter and args.filter not in it["path"]:
            continue
        print(it["path"])
        if it["names"]:
            print("  names:", ", ".join(map(str, it["names"])))
        if it["doc"]:
            print("  doc:", it["doc"])
        print()


if __name__ == "__main__":
    main()
