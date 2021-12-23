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
}
identifiers = ['invoice_number', 'insurance']
mandatory = ['invoice_number']
max_empty_rows = 3
