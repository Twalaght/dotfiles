#!/usr/bin/env python3

import logging
import re
from argparse import ArgumentParser
from datetime import datetime
from pathlib import Path

class Renamer():
	def __init__(self, folder: str):
		self.folder = folder
		unsorted_files = map(str, Path(folder).glob("*.*"))
		self.files = self.natural_sort(unsorted_files)

	@staticmethod
	def natural_sort(unsorted: list) -> list:
		"""Sort a list based on natural counting

		Args:
			files (list): List of strings

		Returns:
			list: Sorted list of strings
		"""
		convert = lambda text: int(text) if text.isdigit() else text.lower()
		alphanumeric_key = lambda key: [convert(x) for x in re.split("([0-9]+)", key)]
		return sorted(unsorted, key = alphanumeric_key)

	def generate_timestamps(self) -> list:
		"""Create a list of file names by their date modified timestamp

		Returns:
			list: Ordered list of names mapped to objects file list
		"""
		new_names = []
		for file_path in self.files:
			# Generate a timestamp string from the files modification time
			last_modified = Path(file_path).stat().st_mtime
			timestamp = datetime.fromtimestamp(last_modified).strftime("%Y%m%d_%H%M%S")

			# Append a counter if the name is not unique
			duplicates = [name for name in new_names if timestamp in name]
			if duplicates: timestamp += f"({len(duplicates) - 1})"
			new_names.append(timestamp)

		return new_names

	def generate_names(self, name: str, offset: int, zeros: int) -> list:
		"""Create a list of incrementing file names

		Args:
			name (str): New name to use, defaults to the parent folder
			offset (int): Starting number to begin numbering files from
			zeros (int): Length of zero padding to use in numbering

		Returns:
			list: Ordered list of names mapped to objects file list
		"""
		# Set zero padding to match number of files, if not provided
		max_len = len(self.files) + offset if offset else 0
		zero_pad = max(len(str(max_len)), 2)
		if zeros and zeros > zero_pad: zero_pad = zeros

		# If name is unset, default to the parent folder
		if not name: name = Path(self.folder).resolve().name

		# If a separator is not used in the name, default to a space
		if name[-1].isalnum(): name += " "

		new_names = []
		for i in range(len(self.files)):
			new_name = f"{name}{str(i + offset).zfill(zero_pad)}"
			new_names.append(new_name)

		return new_names

	@staticmethod
	def prepare(files: list, new_names: list) -> list:
		"""Create list of file rename operations to perform

		Args:
			files (list): Original list of files
			new_names (list): List of names to change the files to

		Returns:
			list: _description_
		"""
		# Ensure input and output lists are the same size
		len_in, len_out = len(files), len(new_names)
		assert len_in == len_out, f"Input length ({len_in}) and output length ({len_out}) did not match"

		operations = []
		for old_file, new_file in zip(files, new_names):
			old_path = Path(old_file)
			new_path = old_path.parent / (new_file + old_path.suffix)
			operations.append([old_path, new_path])

		# Preview the rename operation before it takes place
		preview = lambda paths: print(f"{str(paths[0].name): <{max_width}} -> {str(paths[1].name)}")
		max_width = max([len(str(files[0].name)) for files in operations])

		print("Rename preview:")
		if logger.level >= logging._nameToLevel["WARN"]:
			# Print a short preview if no verbosity argument given
			for paths in operations[:5]: preview(paths)
			print(f"{'': <{max_width}}....")
			for paths in operations[-5:]: preview(paths)
		else:
			# Print additional information as required by logger verbosity
			for paths in operations:
				preview(paths)
				if logger.level <= logging._nameToLevel["DEBUG"]:
					logger.debug(f"{paths[0]} -> {paths[1]}")

		return operations

	@staticmethod
	def execute(operations: list) -> None:
		"""Perform file renaming based on input list

		Args:
			operations (list): List of files to rename and their new names
		"""
		name_pool = [files[0].name for files in operations]

		# Check unique case where new names are identical to original
		if set(name_pool) == {files[1].name for files in operations}: return

		# Cycle through the operations list until it is empty
		while operations:
			tmp = operations.pop(0)

			# Ensure each rename does not overwrite an existing file
			if tmp[1].name not in name_pool:
				logger.debug(f"Renaming {tmp[0]} -> {tmp[1]}")
				Path(tmp[0]).rename(tmp[1])

				# Rename the file in the name pool
				name_pool.remove(tmp[0].name)
				name_pool.append(tmp[1].name)
			else:
				operations.append(tmp)

	def rename(self, time: bool, name: str, offset: int, zeros: int, yes: bool) -> None:
		"""Batch rename the internal list of files

		Args:
			time (bool): Rename files to timestamps of their date modified
			name (str): New name to rename files to
			offset (int): Starting number to begin numbering files from
			zeros (int): Length of zero padding to use in numbering
			yes (bool): Assume yes to the continue prompt if set
		"""
		# Generate new names using the appropriate method
		if time: new_names = self.generate_timestamps()
		else: new_names = self.generate_names(name, offset, zeros)

		# Create list of rename operations
		operations = self.prepare(self.files, new_names)

		# Prompt the user to confirm if the assume yes flag is not present
		if not yes:
			print("Continue with rename? Y/N ", end="")
			response = input().lower()
			if not response or response[0] != "y": return

		# Perform all rename operations
		self.execute(operations)

if __name__ == "__main__":
	# Read the arguments given to the script
	parser = ArgumentParser(description="Mass rename files in a specified folder")
	parser.add_argument("folder", type=str, default=".", help="folder of files to rename")
	parser.add_argument("-t", "--time", action="store_true", help="rename based on timestamps")
	parser.add_argument("-n", "--name", type=str, help="new base name to use")
	parser.add_argument("-o", "--offset", type=int, default=1, help="set starting number")
	parser.add_argument("-z", "--zeros", type=int, help="set zero pad length")
	parser.add_argument("-y", "--yes", action="store_true", help="automatic yes to prompts")
	parser.add_argument("-v", "--verbose", action="count", default=0, help="display debug info")
	args = parser.parse_args()

	logging.basicConfig(format = "%(levelname)s:%(name)s: %(message)s")
	logger = logging.getLogger()

	if args.verbose > 0: logger.setLevel("INFO")
	if args.verbose > 1: logger.setLevel("DEBUG")

	renamer = Renamer(args.folder)
	renamer.rename(args.time, args.name, args.offset, args.zeros, args.yes)
