dbf.py
======

`dbf` provides direct access to dBase III, Foxpro, and Visual Foxpro `.dbf`
files, both reading and writing.  Memo files are supported, as well as binary
character fields and Null fields.  Codepage settings are honored for both field
contents and field names.


Dbf Tables
----------

    table = dbf.Table(
            filename='test_table.dbf',      # path & filename of dbf table
            field_specs=...,                # list of fields if creating new table
            memo_size=128,                  # fixed at 512 for dBase and Clipper
            ignore_memos=False,             # can be set to True if problems with memo file
            codepage=None,                  # temporarily use named codepage
            default_data_types=dict(),      # Python classes to use for data types (e.g. C or N)
            field_data_types=dict(),        # Python classes to use for fields (e.g. name or age)
            dbf_type='db3'                  # type of table [ db3 | clp | fp | vfp ]
            )

`bool(table)` - True if table has any records

`len(table)` - number of records stored in table

`iter(table)` - one record per iteration

`something in table` - record, template, dict, or tuple in table

`table[i]` - the ith record in the table

`table[i:[j][:k]]` - slice of records in table as a dbf.List

`table.add_fields(field_specs)` - adds more fields to existing table

`table.allow_nulls(fields)` - change fields to support Null values

`table.append(data, drop=False, multiple=1)` - 
    - appends data to table
    - data can be a record, template, dict, or tuple
    - if record, template, or dict has fields not present in table a
    - FieldMissingError will be raised unless `drop == True`

`table.backup` - name of last backup created by `create_backup()`

`table.binary_types` - tuple of field types that are stored as binary data (not text)

`table.character_types` - tuple of field types that are stored as text data (not binary)

`table.currency_types` - tuple of field types that hold Currency data

`table.close()` - closes dbf table

`table.codepage [ = xxx]` - returns (or sets) the codepage for the table

`table.create_backup(new_name)` - makes a copy of the table as new\_name (if None, appends \_backup to existing name)

`table.create_index(key)` - creates a temporary, in-memory index using the key function provided

`table.create_template(record=None, **defaults)`
    - creates a template record (templates are also returned by `scatter()`)
    - if `record` or `defaults` are supplied, those values are used to initialize
    - the template, and are what the template is reset back to when `reset()` is
    - called on it

`table.date_types` - tuple of field types that represent a date

`table.datetime_types` - tuple of field types that represent a date and time

`table.delete_fields(field_names)` - permanently removes columns from table

`table.disallow_nulls(fields)` - change fields to not allow Null support

`table.field_count` - number of user fields in table

`table.field_names` - names of the fields as a list (does not include meta-fields `record_number` nor `delete_flag`

`table.filename` - name of file (includes path only if path was passed in)

`table.fixed_types` - tuple of field types that have a fixed amount of data storage in the table

`table.index(x)` - returns first matching record; x == record, template, dict, or tuple

`table.logical_types` - tuple of field types that represent Logical values True, False, and None/Unknown

`table.memo_types` - tuple of field types that are stored in a separate memo file

`table.new(filename, field_specs=None, codepage=None)` - creates a new table as filename; if field\_specs and codepage are not specified the new table will have the same structure and encoding

`table.nullable_field(field)` - returns True if field can store Nulls

`table.numeric_types` - tuple of field types that represent numbers

`table.open(mode=READ_WRITE)` - opens table; other possible mode is `READ_ONLY`

`table.pack()` - physically removes all deleted records from the table (this cannot be undone)

`table.query(criteria)` - brute force search through table; criteria should be a string query (e.g. `select * where name[0] == "E"`)

`table.record_length` - length of one record in bytes

`table.reindex()` - recalculates all indices on table

`table.rename_field(oldname, newname)` - renames a field

`table.resize_field(chosen, new_size)` - resizes fields (C only at this time); creates backup file in TMP, then modifies current structure

`table.structure(fields=None)`
    - return field specification list suitable for creating same table layout
    - fields should be a list of fields or None for all fields in table

`table.use_deleted` - returns (or sets) whether iterations will return records marked as deleted

`table.variable_types` - tuple of field types whose sizes are configurable (e.g. C, N, or F)

`table.version` - returns the table type: dbf, db3, fp, or vfp

`table.zap()` - removes all records from table -- this cannot be undone!


Dbf Lists
---------

    lst = dbf.List(
            records=None,           # initial records to store in list
            desc=None,              # description of list (shows up in repr())
            key=None,               # function that determines record uniqueness
            )                       #  (default is table & record number

`bool(lst)` - True if lst has any records

`len(lst)` - number of records stored in lst

`iter(lst)` - one record per iteration

`something in lst` - record, template, dict, or tuple in lst

`lst[i]` - the ith record in the lst

`lst[i:[j][:k]]` - slice of records in lst as a dbf.List


`lst.append(record)` - adds record to `lst` if `lst.key(record)` not already in `lst`

`lst.clear()` - removes all records from `lst`

`lst.extend(records)` - adds each record to `lst` if `lst.key(record)` not already in `lst`

`lst.index(record)` - returns index of `record` in `lst`

`lst.insert(i, record)` - inserts record into lst at the ith index

`lst.key(record)` - returns key of record

`lst.pop(index=None)`
    - removes and returns the record at index (defaults to last)
    - raises IndexError if list is empty or index is out of range

`lst.query(criteria)`
    - brute force search through lst; see `table.query()`

`lst.remove(record)` - removes first occurance of record -- raises ValueError if not found

`lst.reverse()` - reverses lst

`lst.sort(key=None, reverse=False)` - sorts lst *in-place*; uses `lst.key` by default


Dbf Indices
-----------

    ndx = table.create\_index(key)
        key is a function whose return value is used to sort the records in the
        index (it should return the special value DoNotIndex for records that
        should be completely ignored)

`bool(ndx)` - True if ndx has any records

`len(ndx)` - number of records stored in ndx

`iter(ndx)` - one record per iteration

`something in ndx` - record, template, dict, or tuple in ndx

`ndx[i]` - the ith record in the ndx

`ndx[i:[j][:k]]` - slice of records in ndx as a dbf.List

`ndx.index(record, start=None, stop=None)`
    - returns index of record in ndx
    - start and stop default to 0 and len(ndx)

`ndx.query(criteria)`
    brute force search through ndx; see `table.query()`

`ndx.search(match, partial=False)`
    - returns all records that meet match criteria, which should be a tuple of desired matches
    - uses binary search


Record and Miscellaneous Functions
----------------------------------

`dbf.create_template(record=None, **defaults)`
    - creates a template record (templates are also returned by `scatter()`)
    - if `record` or `defaults` are supplied, those values are used to initialize
    - the template, and are what the template is reset back to when `reset()` is
    - called on it

`dbf.delete(record)` - marks record as deleted

`dbf.export(table_or_records, filename, field_names, format, header, codepage)`
    exports records to a plain text file in either csv, tab, or fixed format    

`dbf.field_names(thing)` - returns fields/keys from records, templates, and dicts

`dbf.gather(record, data, drop=False)` - updates record with data, which should be a
    dict, Record, RecordTemplate.  If `drop` is False and `data` has a field which the
    record does not a FieldMissingError exception is raised.

`dbf.is_deleted(record)` - True if marked as deleted, else False

`dbf.Process(records)` - generator that produces one record per iteration; these
    records are able to have their fields updated individually, and they are written
    to disk at the end of the loop; if an exception occurs, the record is left in its
    pre-generator state (all field updates are discarded)

`dbf.recno(record)` - returns the physical record offset in the file

`dbf.reset(record, keep_fields=None)` - resets the record back to it's original creation
    values, except for keep_fields

`dbf.scan(table, direction='forward', filter=lambda rec: True)`
    adjusts internal record pointer to next record; returns False if there are no more;
    direction can be 'forward' or 'reverse', and filter can be used to skip undesired
    records

`dbf.scatter(record, as_type=create_template)` - returns a RecordTemplate based on record;
    if as_type is 'dict' (or any collections.Mapping on 2.6+) then it is called instead with
    a list of (field, value) tuples; if as_type is any other class it is called with a list
    of record's values; if as_type is anything else it is passed the record directly

`dbf.source_table(record)` - returns the table associated with the record (if called
    with a table, returns the table)

`dbf.undelete(record)` - marks a record as active

`dbf.write(record, **kwargs)` - updates record with kwargs, then writes to disk

Table Navigation for Visual Foxpro Users
----------------------------------------

The Pythonic way to process records is something along the lines of:

    for record in table:
       ...

    or

    data = dbf.List(rec for rec in table if rec.field == 'xxx')
    for record in data:
        ...

However, there is also the more VFPish method:

    table.top()
    while dbf.scan(table):
        record = table.current_record  # gets record at current record pointer
        prev = table.previous_record   # gets record before current pointer
        next = table.next_record       # gets record after current pointer

    while not table.eof():
        table.next()

    or, to move backwards through the table:

    table.bottom()
    while dbf.scan(table, direction='reverse'):
        ...


Dbf Records
-----------

`record = table[x]` 

`bool(record) == True` iif table record, False if Vapor record (record before or after all records in table)

`len(record) == number of fields` (ignores delete flag, \_nullflags, and other system fields)

`iter(record)` == values in record in field order (ignores delete flag, \_nullflags, and other system fields)

`'something' in record` == `'something' in tuple(record)` (value check, not field-name check)


Code Pages
----------

    ascii     - plain ol' ascii
    cp437     - U.S. MS-DOS
    cp850     - International MS-DOS
    cp1252    - Windows ANSI
    mac_roman - Standard Macintosh
    cp865     - Danish OEM
    cp437     - Dutch OEM
    cp850     - Dutch OEM (secondary)
    cp437     - Finnish OEM
    cp437     - French OEM
    cp850     - French OEM (secondary)
    cp437     - German OEM
    cp850     - German OEM (secondary)
    cp437     - Italian OEM
    cp850     - Italian OEM (secondary)
    cp932     - Japanese Shift-JIS
    cp850     - Spanish OEM (secondary)
    cp437     - Swedish OEM
    cp850     - Swedish OEM (secondary)
    cp865     - Norwegian OEM
    cp437     - Spanish OEM
    cp437     - English OEM (Britain)
    cp850     - English OEM (Britain) (secondary)
    cp437     - English OEM (U.S.)
    cp863     - French OEM (Canada)
    cp850     - French OEM (secondary)
    cp852     - Czech OEM
    cp852     - Hungarian OEM
    cp852     - Polish OEM
    cp860     - Portugese OEM
    cp850     - Potugese OEM (secondary)
    cp866     - Russian OEM
    cp850     - English OEM (U.S.) (secondary)
    cp852     - Romanian OEM
    cp936     - Chinese GBK (PRC)
    cp949     - Korean (ANSI/OEM)
    cp950     - Chinese Big 5 (Taiwan)
    cp874     - Thai (ANSI/OEM)
    cp1252    - ANSI
    cp1252    - Western European ANSI
    cp1252    - Spanish ANSI
    cp852     - Eastern European MS-DOS
    cp866     - Russian MS-DOS
    cp865     - Nordic MS-DOS
    cp861     - Icelandic MS-DOS
    cp737     - Greek MS-DOS (437G)
    cp857     - Turkish MS-DOS
    cp950     - Traditional Chinese (Hong Kong SAR, Taiwan) Windows
    cp949     - Korean Windows
    cp936     - Chinese Simplified (PRC, Singapore) Windows
    cp932     - Japanese Windows
    cp874     - Thai Windows
    cp1255    - Hebrew Windows
    cp1256    - Arabic Windows
    cp1250    - Eastern European Windows
    cp1251    - Russian Windows
    cp1254    - Turkish Windows
    cp1253    - Greek Windows
    mac_cyrillic - Russian Macintosh
    mac_latin2 - Macintosh EE
    mac_greek - Greek Macintosh

