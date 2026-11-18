from pathlib import Path
import hashlib
root = Path(__file__).resolve().parent
entries = []
for line in (root / "SHA256SUMS").read_text().splitlines():
    digest, name = line.split("  ", 1)
    p = root / name
    if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest() != digest:
        raise SystemExit("FAIL: " + name)
    entries.append(name)
actual = {str(p.relative_to(root)) for p in root.rglob("*") if p.is_file()
          and p.name != "SHA256SUMS" and "validation" not in p.relative_to(root).parts
          and ".git" not in p.relative_to(root).parts
          and "__pycache__" not in p.parts and p.suffix != ".pyc"}
if set(entries) != actual or len(entries) != len(set(entries)):
    raise SystemExit("FAIL: manifest coverage or duplicate entry")
print("PASS: integrity and coverage for", len(entries), "files")
