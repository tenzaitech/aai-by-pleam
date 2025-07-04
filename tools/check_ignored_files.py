import os
from pathlib import Path

IGNORE_FILES = [
    ".gitignore",
    ".cursorignore",
    ".ignore"
]

def load_ignore_patterns():
    patterns = set()
    for fname in IGNORE_FILES:
        if os.path.exists(fname):
            with open(fname, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        patterns.add(line)
    return patterns

def check_ignored_files(patterns, root="."):
    found = []
    for pattern in patterns:
        for path in Path(root).glob(pattern):
            if path.exists():
                found.append(str(path))
    return found

if __name__ == "__main__":
    patterns = load_ignore_patterns()
    if not patterns:
        print("ไม่พบไฟล์ ignore ใด ๆ ในโปรเจกต์นี้")
    else:
        found = check_ignored_files(patterns)
        if found:
            print("ไฟล์/โฟลเดอร์ที่ควร ignore แต่ยังอยู่ใน workspace:")
            for f in found:
                print(" -", f)
        else:
            print("ไม่พบไฟล์/โฟลเดอร์ที่ควร ignore ใน workspace") 