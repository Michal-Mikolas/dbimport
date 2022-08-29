import re
from datetime import datetime

def fixval(v, row):
	if v in ('NULL', 'None'):
		v = None
	return v


inbox = 'inbox'
outbox = 'outbox'
db = 'postgresql://user:pass@server:5432/database'
table = 'invoices'
skip = 1
columns = {
	'date_from': 'A',
	'date_to': 'B',
	'invoice_number': 'C',
	'order_number': 'D',
	'insurance': 'E',
	'icz': ['F', lambda v, row: int(v.replace('-', '')) if v else None],
	'created_date': 'G',
	'payment_date': 'H',
	'paid_date': 'I',
	'amount': 'J',
	'paid_amount': 'K',
	'points': 'M',
	'score': 'N',
	'updated_at': ['B', lambda v: datetime.now()],
}
identifiers = ['invoice_number', 'insurance']
mandatory = ['invoice_number']
after_insert = {
	'created_at': lambda: datetime.now(),
}
max_empty_rows = 3
