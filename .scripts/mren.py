#!/usr/bin/python3

from argparse import ArgumentParser
from pathlib import Path
from re import split as resplit

# Read the arguments given to the script
parser = ArgumentParser(description="Mass rename files in a specified folder")
parser.add_argument("target", metavar="folder", type=str, help="folder of files to rename")
parser.add_argument("name", metavar="new name", type=str, help="new name for the files")
parser.add_argument("-z", "--zeros", type=int, help="set the length of zero padding")
parser.add_argument("-o", "--offset", type=int, default=1, help="set the starting number")
parser.add_argument("-v", "--verbose", action="store_true", help="display full rename preview")
args = parser.parse_args()

# Sort file names by natural counting
def natural_sort(input_list):
	convert = lambda text: int(text) if text.isdigit() else text.lower()
	alphanum_key = lambda key: [convert(x) for x in resplit("([0-9]+)", key)]
	return sorted(input_list, key=alphanum_key)

# Display the old and new names for a give set of files
def preview(files, width):
	for f in files:
		original = f"{f['old_name']}.{f['ext']}"
		new = f"{f['new_name']}.{f['ext']}"
		print(f"{original: <{width}} -> {new}")

# Build and sort the file list into a dictionary
files = [str(x) for x in Path(args.target).glob("*.*")]
files = natural_sort(files)
# files = [{"path": x} for x in files]

# Determine the required zero padding for new file names
max_len = len(files) + args.offset if args.offset else 0
pad = max(len(str(max_len)), 2)
if args.zeros and args.zeros > pad: pad = args.zeros

# Update each files dictionary entry with extension and both names
for i in range(len(files)):
	path = files[i].rsplit("/", 1)[0]
	old_name, ext = str(files[i]).split("/")[-1].rsplit(".", 1)
	new_name = f"{args.name}{str(i + args.offset).zfill(pad)}"
	files[i] = {"path": path, "ext": ext, "old_name": old_name, "new_name": new_name}

# Preview the rename operation before it takes place
print("Rename preview:")
max_width = max([len(f"{x['old_name']}.{x['ext']}") for x in files])
if args.verbose or len(files) <= 20:
	preview(files, max_width)
else:
	preview(files[:10], max_width)
	print(f"{'': <{max_width}}....")
	preview(files[-10:], max_width)

# Check for response to continue with the rename job
print("\nContinue with rename? Y/N")
response = input().lower()
if not response or response[0] != "y": exit()

# Rename process
old_paths = [Path(f["path"]) / f"{f['old_name']}.{f['ext']}" for f in files]
new_paths = [Path(f["path"]) / f"{f['new_name']}.{f['ext']}" for f in files]
for i in range(len(old_paths)): Path(old_paths[i]).rename(new_paths[i])

# Prompt the user to revert if required
print("\nKeep changes? Y/N")
response = input().lower()
if response and response[0] == "y": exit()
print("Reverting changes")
for i in range(len(old_paths)): Path(new_paths[i]).rename(old_paths[i])
