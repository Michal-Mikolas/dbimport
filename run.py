import dataset
import openpyxl
from tools import Tools
import os

#~~~~~~ Import config file
import sys
import importlib.util
import argparse

# Parse arguments
parser = argparse.ArgumentParser(description='Import xlsx to DB defined in config file.')
parser.add_argument('config', help='Path to configuration file')
args = parser.parse_args()

# Load config
config_file = args.config
if not os.path.isfile(config_file) and os.path.isfile(config_file + '.py'):
	config_file += '.py'

if not os.path.isfile(config_file):
	print(f"Error: Config file '{args.config}' not found.")
	sys.exit(1)

# Import config file
spec = importlib.util.spec_from_file_location("conf", config_file)
conf = importlib.util.module_from_spec(spec)
try:
	spec.loader.exec_module(conf)
except Exception as e:
	print(f"Error loading config file '{config_file}': {e}")
	sys.exit(1)
#~~~~~~/


######
#     # #    # #    #
#     # #    # ##   #
######  #    # # #  #
#   #   #    # #  # #
#    #  #    # #   ##
#     #  ####  #    #

db = dataset.connect(conf.db)

for file in Tools.find_files(f'{conf.inbox}/*.xlsx'):
	Tools.log(file)
	conf.file = os.path.split(file)[1]

	wb = openpyxl.load_workbook(file, read_only=True)
	ws = wb.active

	db.begin()

	r = conf.skip + 1 if (type(conf.skip) is int) else 1
	success_counter = 0
	empty_rows_counter = 0
	for row in ws.iter_rows(min_row=r):
		#
		# Init
		#
		r += 1

		#
		# Get data
		#
		entry = {}
		for name, column in conf.columns.items():
			# Prepare column letter and callback
			if not column:
				continue
			elif type(column).__name__ == 'str':
				column_letter = column
				column_callback = lambda v: v
			else:
				column_letter = column[0]
				column_callback = column[1]

			# Get value
			try:
				v = row[Tools.col_num(column_letter)-1].value
			except IndexError:
				v = None

			if column_callback.__code__.co_argcount == 0:
				v = column_callback()
			if column_callback.__code__.co_argcount == 1:
				v = column_callback(v)
			if column_callback.__code__.co_argcount == 2:
				v = column_callback(v, row)

			if v is not None:
				entry[name] = v

		#
		# Skips & Checks
		#
		check = True
		for column in conf.mandatory:
			if not entry.get(column):
				check = False
				empty_rows_counter += 1
				break

		if empty_rows_counter >= conf.max_empty_rows:
			break

		# Skip first rows
		if (type(conf.skip).__name__ == 'function') and (conf.skip(entry)):
			empty_rows_counter += 1
			continue

		#
		# Save to DB
		#
		if check:
			inserted_id = db[conf.table].upsert(entry, conf.identifiers)  # returns True for update, ID for insert

			#~~~~~~ Values after insert (aka `created_at` column)
			if (type(inserted_id) == int):
				try:
					values = {'id': inserted_id}
					for column, value in conf.after_insert.items():
						values[column] = value() if (type(value).__name__ == 'function') else value

					db[conf.table].update(values, ['id'])
				except AttributeError:
					pass
			#~~~~~~/

			success_counter += 1

		#~~~~~~ Chunks
		if 'chunk' in dir(conf):
			if r % conf.chunk == 0:
				db.commit()
				Tools.log('- {:,d} rows done'.format(r).replace(',', ' '))
				db.begin()
		#~~~~~~/

	db.commit()

	outbox_path = f'{conf.outbox}/{Tools.remove_dirs(file)}'
	os.unlink(outbox_path) if os.path.isfile(outbox_path) else None
	os.rename(file, outbox_path)

	Tools.log(f'...done {success_counter} rows\n')

Tools.log('Done.')
