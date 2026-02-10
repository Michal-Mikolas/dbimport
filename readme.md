# Universal Excel to DB Importer

A flexible tool to import Excel (`.xlsx`) files into any relational database. It moves processed files to an outbox and handles column mapping, data transformation, and deduplication via configuration files.

## Features

- **Universal Database Support**: Works with PostgreSQL, MySQL, SQLite, etc. (uses `dataset` / SQLAlchemy).
- **Flexible Mapping**: Map Excel columns to Database columns with optional transformation functions.
- **Deduplication**: Supports "upsert" operations based on unique identifiers.
- **Workflow**: Automatically moves processed files from an `inbox` to an `outbox` folder.
- **Performance**: configurable transaction chunking for large datasets.

## Installation

1. **Requirements**
   Ensure you have Python installed. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. **Database Driver**
   `requirements.txt` includes `psycopg2` for PostgreSQL. If you use another database (e.g., MySQL), install the appropriate driver (e.g., `mysqlclient` or `pymysql`).

## Usage

1. **Prepare Configuration**
   Create a configuration file (e.g., `my_config.py`) defining your database connection and mapping. You can use `config.example.py` as a template.

2. **Prepare Files**
   Place your `.xlsx` files into the configured `inbox` directory.

3. **Run Importer**
   Run the script passing your configuration file name (with or without `.py` extension):
   ```bash
   python run.py my_config
   ```

## Configuration

The configuration file is a Python script that defines the import behavior. See `config.example.py` for a full example.

### Key Settings

- **db**: Database connection string (e.g., `'postgresql://user:pass@localhost:5432/mydb'`).
- **table**: Target database table name.
- **inbox / outbox**: Directories for source and processed files.
- **skip**: Number of header rows to skip in the Excel file.

### Column Mapping (`columns`)

Dictionary where keys are **Database Columns** and values are **Excel Mappings**:

```python
columns = {
    # Simple mapping: DB column 'name' <- Excel column 'A'
    'name': 'A',

    # Transformation: DB column 'age' <- Excel 'B', converted to integer
    'age': ['B', lambda v: int(v) if v else 0],

    # Advanced: Use row data or external logic
    'imported_at': ['A', lambda: datetime.now()],
}
```

### Callbacks
Tranformation functions can accept:
- **0 arguments**: e.g. `lambda: datetime.now()`
- **1 argument** (Value of the cell): e.g. `lambda v: v.strip()`
- **2 arguments** (Value, Row object): e.g. `lambda v, row: row[0].value`

### Deduplication
- **identifiers**: List of columns used to identify unique rows for UPSERT (Update/Insert) operations.
