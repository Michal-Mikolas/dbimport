import dataset
import openpyxl
from tools import Tools
import os

# import config_dose_entries as conf
# import config_dose_entries_archive as conf
# import config_invoices as conf
# import config_company_file as conf
# import config_company_alias as conf
import config_dan_davky as conf


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
	for row in ws.iter_rows(min_row = (conf.skip + 1 if conf.skip else 1)):
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
			v = row[Tools.col_num(column_letter)-1].value

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
