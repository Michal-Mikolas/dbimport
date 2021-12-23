import dataset
import openpyxl
from tools import Tools
import os

import config_dose_entries as conf


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

	wb = openpyxl.load_workbook(file)
	ws = wb.active

	r = 0
	success_counter = 0
	empty_rows_counter = 0
	while True:
		#
		# Init
		#
		r += 1

		#
		# Get data
		#
		entry = {}
		for name, column in conf.columns.items():
			if not column:
				continue
			elif type(column).__name__ == 'str':
				column_letter = column
				column_callback = lambda v: v
			else:
				column_letter = column[0]
				column_callback = column[1]

			v = ws.cell(r, Tools.col_num(column_letter)).value
			v = column_callback(v)
			if v:
				entry[name] = column_callback(v)

		#
		# Skips & Checks
		#
		check = True
		for column in conf.mandatory:
			if not entry.get(column):
				check = False
				empty_rows_counter += 1

		if empty_rows_counter >= conf.max_empty_rows:
			break

		if (type(conf.skip) == int) and (r <= conf.skip):
			continue
		if (type(conf.skip).__name__ == 'function') and (conf.skip(entry)):
			continue

		#
		# Save to DB
		#
		if check:
			db[conf.table].upsert(entry, conf.identifiers)
			success_counter += 1

	outbox_path = f'{conf.outbox}/{Tools.remove_dirs(file)}'
	os.unlink(outbox_path) if os.path.isfile(outbox_path) else None
	os.rename(file, outbox_path)

	Tools.log(f'...done {success_counter} rows\n')

Tools.log('Done.')
