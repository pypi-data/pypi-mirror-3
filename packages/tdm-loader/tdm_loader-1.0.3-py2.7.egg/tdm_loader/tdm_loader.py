"""This module allows National Instruments TDM/TDX files to be accessed like
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
"""
import os.path
from xml.etree import cElementTree as etree

import numpy as np
try:
    from matplotlib import pyplot as plt
    plt_available = True
except ImportError:
    plt_available = False


__all__ = ('OpenFile', 'ReadTDM')


# XML "QName" in the TDM file
# there has to be an easy way to determine this programmatically
QNAME = '{http://www.ni.com/Schemas/USI/1_0}'


# dictionary for converting from NI to NumPy datatypes
DTYPE_CONVERTERS = {'eInt8Usi':    'i1',
                    'eInt16Usi':   'i2',
                    'eInt32Usi':   'i4',
                    'eInt64Usi':   'i8',
                    'eUInt32Usi':  'u4',
                    'eUInt64Usi':  'u8',
                    'eFloat32Usi': 'f4',
                    'eFloat64Usi': 'f8'}


class OpenFile(object):
    """Class for opening a National Instruments TDM/TDX file.

    Parameters
    ----------
    tdm_path : str
        The full path to the .TDM file.
    tdx_path : str, Optional
        The full path to the .TDX file.  If not present, it will be assumed the
        TDX file is located in the same directory as the .TDM file, and the
        filename specified in the .TDM file will be used.
    """
    def __init__(self, tdm_path, tdx_path=''):
        self._folder, self._tdm_filename = os.path.split(tdm_path)
        self.tdm = ReadTDM(tdm_path)
        self.num_channels = self.tdm.num_channels

        if tdx_path == '':
            self._tdx_path = os.path.join(self._folder, self.tdm.tdx_filename)
        else:
            self._tdx_path = tdx_path
        self._open_tdx(self._tdx_path)
        self.channel_names = [chan.name for chan in self.tdm.channels]

    def _open_tdx(self, tdx_path):
        """Open a TDX file.
        """
        try:
            self._tdx_fobj = open(tdx_path, mode='rb')
        except IOError:
            raise IOError('TDX file not found: ' + tdx_path)
        if self.tdm.exporter_type.find('National Instruments') >= 0:
            # data is in column first order
            # use the hacked solution for the memmap
            self._tdx_memmap = MemmapColumnFirst(self._tdx_fobj, self.tdm)
            self._memmap_type = 'Slow'
        elif self.tdm.exporter_type.find('LabVIEW') >= 0 or \
                self.tdm.exporter_type.find('Data Server') >= 0:
            # data is in row first order
            # use the NumPy memmap directly (almost)
            self._tdx_memmap = MemmapRowFirst(self._tdx_fobj, self.tdm)
            self._memmap_type = 'Fast'
        else:
            message = 'unknown exporter type: {exp_type}'
            raise IOError(message.format(exp_type=self.tdm.exporter_type))

    def channel_lookup(self, channel_name):
        """Return the column index for the named channel

        Parameters
        ----------
        channel_name : str
            The name to lookup. The results are independent of case and spaces in the name.

        Returns
        -------
        index : int
            Returns the column index or -1 if the channel is not found.
        """
        try:
            return self.channel_names.index(channel_name) # exact match
        except ValueError:
            pass
        try: # independent of case
            channel_names = [name.upper() for name in self.channel_names]
            return channel_names.index(channel_name.upper())
        except ValueError:
            pass
        try: # independent of case and spaces
            channel_names = [name.replace(' ','') for name in channel_names]
            return channel_names.index(channel_name.upper().replace(' ',''))
        except ValueError:
            return -1

    def channel_search(self, search_term):
        """Returns a list of channel names that contain ``search term``.
        Results are independent of case and spaces in the channel name.
        """
        search_term = search_term.upper().replace(' ','')
        return [name for name in self.channel_names if
                            name.upper().replace(' ','').find(search_term) >= 0]

    def __getitem__(self, key):
        return self._tdx_memmap.__getitem__(key)

    def __len__(self):
        return self._tdx_memmap.__len__()

    def plot_channels(self, x_channel, y_channels):
        """Plot multiple channels.

        Parameters
        ----------
        x_channel : str
            The string name of a single channel to plot on the x-axis.
        y_channels : list of str
            A list of multiple string channel names to plot on the y-axis.
        """
        if plt_available:
            x_data = [self[x_channel]] * len(y_channels)
            y_data = [self[channel] for channel in y_channels]
            for i in xrange(len(y_channels)):
                plt.plot(x_data[i], y_data[i])
            plt.grid()
            plt.show()
        else:
            raise NotImplementedError(('matplotlib must be installed for '
                                       'plotting'))

    def col(self, column_number):
        """Returns a data column by its index number.
        """
        return self._tdx_memmap.col(column_number)

    def close(self):
        """Close the file.
        """
        self._tdx_fobj.close()

    def __del__(self):
        self.close()

    def __repr__(self):
        return ''.join(['NI TDM-TDX file\n',
                       'TDM Path: ', os.path.join(self._folder,
                                                  self._tdm_filename),
                       '\nTDX Path: ', self._tdx_path, '\n',
                       'Number of Channels: ',str(self.num_channels), '\n',
                       'Channel Length: ', str(len(self)), '\n',
                       'Memory Map Type: ', self._memmap_type])


class MemmapRowFirst(object):
    """Wrapper class for opening row-ordered TDX files.  This is only needed
    because NumPy memmap objects don't support [i,j] style indexing.
    """
    def __init__(self, fobj, tdm_file):
        self._memmap = np.memmap(fobj, dtype=tdm_file.dtype,
                                 mode='r').view(np.recarray)
        self._col2name = {}
        for i, channel in enumerate(tdm_file.channels):
            self._col2name[i] = channel.name

    def __getitem__(self, key):
        try:
            slices = key.indices(self.__len__()) # input is a slice object
            ind = range(slices[0], slices[1], slices[2])
            return self._memmap[ind]
        except AttributeError:
            pass
        try:
            return self._memmap[key] # input is a row number or column name
        except IndexError:
            return self._memmap[key[0]][key[1]] # input is a tuple

    def __len__(self):
        return len(self._memmap)

    def col(self, col_num):
        """Returns a data column by its index number.
        """
        return self._memmap[self._col2name[col_num]]


class MemmapColumnFirst(object):
    """Wrapper class for opening column-ordered TDX files.
    """
    def __init__(self, fobj, tdm_file):
        self._memmap = []
        self._name2col = {}
        self._col2name = {}
        self._num_channels = tdm_file.num_channels
        self._empty_row = np.recarray((1, ), tdm_file.dtype)
        self._empty_row[0] = '' # initialize all items to zero
        channels = tdm_file.channels
        for i in xrange(len(channels)):
            self._name2col[channels[i].name] = i
            self._col2name[i] = channels[i].name
            self._memmap.append(np.memmap(fobj,
                                          offset=channels[i].byte_offset,
                                          shape=(channels[i].length, ),
                                          dtype=channels[i].dtype,
                                          mode='r').view(np.recarray))

    def __getitem__(self, key):
        try:
            slices = key.indices(self.__len__()) # input is a slice object
            ind = range(slices[0], slices[1], slices[2])
            row = self._empty_row.copy()
            row = np.resize(row, (len(ind), ))
            for rowi, i in enumerate(ind):
                for j in xrange(self._num_channels):
                    row[rowi][self._col2name[j]] = self._memmap[j][i]
            return row
        except AttributeError:
            pass
        try:
            return self._memmap[self._name2col[key]] # input is a column name
        except KeyError:
            pass
        try:
            return self._memmap[key[1]][key[0]] # input is a tuple
        except TypeError:
            pass
        row = self._empty_row.copy() # input is a row number
        for j in xrange(self._num_channels):
            row[0][self._col2name[j]] = self._memmap[j][key]
        return row[0]

    def __len__(self):
        return len(self._memmap[0])

    def col(self, col_num):
        """Returns a data column by its index number.
        """
        return self._memmap[col_num]


class ReadTDM(object):
    """Class for parsing and storing data from a .TDM file.

    Parameters
    ----------
    tdm_path : str
        The full path to the .TDM file.
    """
    def __init__(self, tdm_path):
        try:
            string = open(tdm_path, mode='r').read()
        except IOError:
            raise IOError('TDM file not found: ' + tdm_path)
        self._xmltree = etree.XML(string)
        self._extract_file_props()
        self._extract_channel_props()
        self._xmltree.clear()

    def _extract_file_props(self):
        """Extracts file data from a TDM file.
        """
        self.exporter_type = self._xmltree.find(QNAME + 'documentation')\
                                                  .find(QNAME + 'exporter').text

        fileprops = self._xmltree.find(QNAME + 'include').find('file')
        self.tdx_filename = fileprops.get('url')
        self.byte_order = fileprops.get('byteOrder')
        if self.byte_order == 'littleEndian':
            self._endian = '<'
        elif self.byte_order == 'bigEndian':
            self._endian = '>'
        else:
            raise TypeError('Unknown endian format in TDM file')

    def _extract_channel_props(self):
        """Extracts channel data from a TDM file.
        """
        temp = self._xmltree.find(QNAME + 'include').find('file')
        blocks = temp.findall('block_bm')
        if len(blocks) == 0:
            blocks = temp.findall('block')
        channel_names = self._xmltree.find(QNAME + 'data').findall(
                                                                  'tdm_channel')
        self.num_channels = len(blocks)
        assert(len(blocks) == len(channel_names))

        formats = []
        names = []
        self.channels = []
        for i in xrange(self.num_channels):
            chan = ChannelData()
            chan.byte_offset = int(blocks[i].get('byteOffset'))
            chan.length = int(blocks[i].get('length'))
            try:
                chan.dtype = self._convert_dtypes(blocks[i].get('valueType'))
            except KeyError:
                raise TypeError(
                            'Unknown data type in TDM file. Channel ' + str(i))
            chan.name = str(channel_names[i].find('name').text)
            self.channels.append(chan)
            formats.append(chan.dtype)
            names.append(chan.name)

        self.dtype = np.format_parser(formats, names, []).dtype

    def _convert_dtypes(self, tdm_dtype):
        """Convert a TDM data type to a NumPy data type.
        """
        # this will need to be adjusted to work with strings
        # "endianness" doesn't matter, so NumPy uses the '|' symbol
        return self._endian + DTYPE_CONVERTERS[tdm_dtype]


class ChannelData(object):
    """Stores data about a single data channel.
    """
    def __init__(self):
        self.name = ''
        self.dtype = ''
        self.length = 0
        self.byte_offset = 0

    def __repr__(self):
        return ''.join(['name = ', self.name, '\ndtype = ', self.dtype, '\n',
                        'length = ', str(self.length), '\n',
                        'byte offset = ', str(self.byte_offset)])
