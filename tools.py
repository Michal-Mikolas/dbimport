from datetime import datetime
import os
from glob import glob

class Tools:

	def find_files(mask):
		files = []
		for file in glob(mask):
			if os.path.isdir(file):
				continue

			files.append(file)

		return files

	def now_str():
		return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

	def remove_dirs(path):
		path_parts = os.path.split(path)
		return path_parts[-1]

	def log(msg):
		print("[{:s}] {:s}".format(
			Tools.now_str(),
			msg
		))

	def col_num(name):
		"""Excel-style column name to number, e.g., A = 1, Z = 26, AA = 27, AAA = 703."""
		"""https://stackoverflow.com/questions/7261936/convert-an-excel-or-spreadsheet-column-letter-to-its-number-in-pythonic-fashion"""
		n = 0
		for c in name:
			n = n * 26 + 1 + ord(c) - ord('A')
		return n
