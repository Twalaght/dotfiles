#!/usr/bin/python3

import hashlib
from argparse import ArgumentParser
from pathlib import Path

parser = ArgumentParser(description="Find duplicate files by hash")
parser.add_argument("target", metavar="folder", type=str, help="folder to be checked")
args = parser.parse_args()

# Return the md5 hash of a file
def md5(path):
	hash_md5 = hashlib.md5()
	with open(path, "rb") as f:
		while True:
			chunk = f.read(4096)
			if not chunk: break
			hash_md5.update(chunk)

	return hash_md5.hexdigest()

# Get full set of files from a path
def iter_files(path):
	return [item for item in path.rglob("*") if item.is_file()]

# Hash each file and record unique hashes
table = {}
files = iter_files(Path(args.target))
for i in range(len(files)):
	print(f"Hashing {i + 1}/{len(files)}", end = "\r")

	hash_md5 = md5(files[i])
	if hash_md5 in table:
		table[hash_md5].append(str(files[i]))
	else:
		table[hash_md5] = [str(files[i])]

print("\n")

# Find duplicate files and print them
dupes = []
for v in table.values():
	if len(v) > 1:
		dupes.append(v)

for i in range(len(dupes)):
	print(f"Duplicate group {i + 1}")
	for d in dupes[i]: print(f"\t{d}")
