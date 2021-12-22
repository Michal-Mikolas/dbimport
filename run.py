import dataset
import openpyxl
from tools import Tools
import os

import config_invoices as conf

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
    empty_rows_counter = 0
    while True:
        #
        # Init
        #
        r += 1

        if r <= conf.skip:
            continue

        #
        # Get data
        #
        entry = {}
        for name, column in conf.columns.items():
            if type(column).__name__ == 'str':
                column_letter = column
                column_callback = lambda v: v
            else:
                column_letter = column[0]
                column_callback = column[1]

            v = ws.cell(r, Tools.col_num(column_letter)).value
            entry[name] = column_callback(v)

        #
        # Check
        #
        check = True
        for column in conf.mandatory:
            if not entry[column]:
                check = False
                empty_rows_counter += 1

        if empty_rows_counter >= 3:
            break

        #
        # Save to DB
        #
        if check:
            db[conf.table].upsert(entry, conf.identifiers)

    outbox_path = f'{conf.outbox}/{Tools.remove_dirs(file)}'
    os.unlink(outbox_path) if os.path.isfile(outbox_path) else None
    os.rename(file, outbox_path)

    Tools.log(f'...done {r-conf.skip-3} rows\n')

Tools.log('Done.')
