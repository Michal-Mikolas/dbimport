import re
from datetime import datetime, date

def fixval(v, row):
	if v in ('NULL', 'None'):
		v = None
	return v

def fixstr(v, row):
	v = fixval(v, row)
	return str(v)

def fixdate(v):
	if type(v) == str and re.match('\d+\.\d+\.\d+', v):
		return datetime.strptime(v, '%d.%m.%Y')

	if type(v) in [datetime, date]:
		return v

	return None


file = ''  # will be filled later automatiucally

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
	'icz': ['F', lambda v: int(v.replace('-', '')) if v else None],
	'created_date': 'G',
	'payment_date': 'H',
	'paid_date': 'I',
	'amount': 'J',
	'paid_amount': 'K',
	'points': 'M',
	'score': 'N',
	'updated_at': ['B', lambda v, row: datetime.now()],
	'file': ['B', lambda: file],
}
identifiers = ['invoice_number', 'insurance']
mandatory = ['invoice_number']
after_insert = {
	'created_at': lambda: datetime.now(),
}
max_empty_rows = 3
