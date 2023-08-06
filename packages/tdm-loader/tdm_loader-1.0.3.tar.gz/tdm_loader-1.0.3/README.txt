This module allows National Instruments TDM/TDX files to be accessed like
NumPy structured arrays.

It can be installed in the standard way::

    python setup.py install

Sample usage::

    import tdm_loader
    data_file = tdm_loader.OpenFile('filename.tdm')

Access a row::

    data_file[row_num]

Access a column by name::

    data_file[column_name]

Access a column by number::

    data_file.col(column_num)

Search for a column name.  A list of all column names that contain
``search_term`` will be returned::

    data_file.channel_search(search_term)
