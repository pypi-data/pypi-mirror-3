#! /usr/bin/env python
# Last Change: Wed Oct 03 05:00 PM 2007 J

# Copyright (C) 2006-2007 Cournapeau David <cournape@gmail.com>
#
# This library is free software; you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 2.1 of the License, or (at your option)
# any later version.
# 
# This library is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
# 
# You should have received a copy of the GNU Lesser General Public License
# along with this library; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

# vim:syntax=python

# TODO:
#   - import format classes so that we get meaningful information from an
#   existing format
#   - better API for reader/writer, including integer formats and partial
#   reading
#   - ability to get log of sndfile ?
#   - check how to play sound under windows, OS X and other UNIX

"""This module implements the wrappers around libsndfile."""

__docformat__ = 'restructuredtext'

#__all__ = ['sndfile', 'formatinfo']

import copy
import warnings

#================
# Load libsndfile
#================
import ctypes
from ctypes import cdll, Structure, c_int, pointer, POINTER, \
        create_string_buffer, c_char_p, sizeof, string_at
try:
    from ctypes import c_int64
except ImportError, e:
    print "Cannot import c_int64 from ctypes: if you are on ubuntu/debian," +\
        " this is likely because ctypes was compiled with libffi. see" +\
        " https://launchpad.net/ubuntu/+source/python2.5/+bug/71914"
    raise e

from numpy.ctypeslib import ndpointer
CTYPES_MAJOR    = int(ctypes.__version__.split('.')[0])
CTYPES_MINOR    = int(ctypes.__version__.split('.')[1])
CTYPES_MICRO    = int(ctypes.__version__.split('.')[2])
if CTYPES_MAJOR < 1 or (CTYPES_MINOR == 0 and CTYPES_MICRO < 1):
    raise ImportError("version of ctypes is %s, expected at least %s" \
            % (ctypes.__version__, '1.0.1'))
import numpy as N

_SND = cdll.LoadLibrary('libsndfile.so.1')

#=========================
# Definition of constants
#=========================
# READ/WRITE Mode
SFM = {
	'SFM_WRITE'	: 0x20,
	'SFM_RDWR'	: 0x30,
	'SFM_READ'	: 0x10
}

# SF BOOL
SF_BOOL = {
	'SF_TRUE'	: 1,
	'SF_FALSE'	: 0
}

# Format
SF_FORMAT = {
	'SF_FORMAT_VOX_ADPCM'	: 0x0021,
	'SF_FORMAT_FLOAT'	: 0x0006,
	'SF_FORMAT_PCM_S8'	: 0x0001,
	'SF_FORMAT_IMA_ADPCM'	: 0x0012,
	'SF_FORMAT_SVX'	: 0x060000,
	'SF_FORMAT_VOC'	: 0x080000,
	'SF_FORMAT_PCM_U8'	: 0x0005,
	'SF_FORMAT_ALAW'	: 0x0011,
	'SF_FORMAT_G721_32'	: 0x0030,
	'SF_FORMAT_DWVW_N'	: 0x0043,
	'SF_FORMAT_WAV'	: 0x010000,
	'SF_FORMAT_SD2'	: 0x160000,
	'SF_FORMAT_HTK'	: 0x100000,
	'SF_FORMAT_ENDMASK'	: 0x30000000,
	'SF_FORMAT_DPCM_16'	: 0x0051,
	'SF_FORMAT_DWVW_24'	: 0x0042,
	'SF_FORMAT_PCM_32'	: 0x0004,
	'SF_FORMAT_WAVEX'	: 0x130000,
	'SF_FORMAT_DOUBLE'	: 0x0007,
	'SF_FORMAT_NIST'	: 0x070000,
	'SF_FORMAT_PCM_16'	: 0x0002,
	'SF_FORMAT_RAW'	: 0x040000,
	'SF_FORMAT_W64'	: 0x0B0000,
	'SF_FORMAT_PVF'	: 0x0E0000,
	'SF_FORMAT_AU'	: 0x030000,
	'SF_FORMAT_GSM610'	: 0x0020,
	'SF_FORMAT_CAF'	: 0x180000,
	'SF_FORMAT_PAF'	: 0x050000,
	'SF_FORMAT_ULAW'	: 0x0010,
	'SF_FORMAT_MAT4'	: 0x0C0000,
	'SF_FORMAT_MAT5'	: 0x0D0000,
	'SF_FORMAT_XI'	: 0x0F0000,
	'SF_FORMAT_SUBMASK'	: 0x0000FFFF,
	'SF_FORMAT_DPCM_8'	: 0x0050,
	'SF_FORMAT_G723_24'	: 0x0031,
	'SF_FORMAT_G723_40'	: 0x0032,
	'SF_FORMAT_DWVW_16'	: 0x0041,
	'SF_FORMAT_AIFF'	: 0x020000,
	'SF_FORMAT_DWVW_12'	: 0x0040,
	'SF_FORMAT_TYPEMASK'	: 0x0FFF0000,
	'SF_FORMAT_FLAC'	: 0x170000,
	'SF_FORMAT_PCM_24'	: 0x0003,
	'SF_FORMAT_SDS'	: 0x110000,
	'SF_FORMAT_IRCAM'	: 0x0A0000,
	'SF_FORMAT_MS_ADPCM'	: 0x0013,
	'SF_FORMAT_AVR'	: 0x120000
}

# ENDIANESS
SF_ENDIAN = {
	'SF_ENDIAN_BIG'	: 0x20000000,
	'SF_ENDIAN_FILE'	: 0x00000000,
	'SF_ENDIAN_LITTLE'	: 0x10000000,
	'SF_ENDIAN_CPU'	: 0x30000000
}

# Commands
SF_COMMAND = {
	'SFC_GET_LIB_VERSION'	: 0x1000,
	'SFC_CALC_SIGNAL_MAX'	: 0x1040,
	'SFC_GET_DITHER_INFO'	: 0x10A3,
	'SFC_GET_LOG_INFO'	: 0x1001,
	'SFC_GET_FORMAT_SUBTYPE_COUNT'	: 0x1032,
	'SFC_FILE_TRUNCATE'	: 0x1080,
	'SFC_GET_INSTRUMENT'	: 0x10D0,
	'SFC_UPDATE_HEADER_NOW'	: 0x1060,
	'SFC_SET_DITHER_ON_WRITE'	: 0x10A0,
	'SFC_SET_NORM_DOUBLE'	: 0x1012,
	'SFC_GET_CLIPPING'	: 0x10C1,
	'SFC_SET_RAW_START_OFFSET'	: 0x1090,
	'SFC_CALC_NORM_MAX_ALL_CHANNELS'	: 0x1043,
	'SFC_SET_NORM_FLOAT'	: 0x1013,
	'SFC_SET_ADD_DITHER_ON_WRITE'	: 0x1070,
	'SFC_GET_NORM_FLOAT'	: 0x1011,
	'SFC_GET_SIGNAL_MAX'	: 0x1044,
	'SFC_GET_MAX_ALL_CHANNELS'	: 0x1045,
	'SFC_GET_FORMAT_MAJOR'	: 0x1031,
	'SFC_SET_INSTRUMENT'	: 0x10D1,
	'SFC_CALC_MAX_ALL_CHANNELS'	: 0x1042,
	'SFC_GET_DITHER_INFO_COUNT'	: 0x10A2,
	'SFC_SET_BROADCAST_INFO'	: 0x10F1,
	'SFC_SET_DITHER_ON_READ'	: 0x10A1,
	'SFC_GET_FORMAT_MAJOR_COUNT'	: 0x1030,
	'SFC_GET_FORMAT_INFO'	: 0x1028,
	'SFC_GET_SIMPLE_FORMAT_COUNT'	: 0x1020,
	'SFC_CALC_NORM_SIGNAL_MAX'	: 0x1041,
	'SFC_GET_LOOP_INFO'	: 0x10E0,
	'SFC_SET_ADD_PEAK_CHUNK'	: 0x1050,
	'SFC_SET_ADD_DITHER_ON_READ'	: 0x1071,
	'SFC_SET_SCALE_FLOAT_INT_READ'	: 0x1014,
	'SFC_GET_FORMAT_SUBTYPE'	: 0x1033,
	'SFC_TEST_IEEE_FLOAT_REPLACE'	: 0x6001,
	'SFC_SET_UPDATE_HEADER_AUTO'	: 0x1061,
	'SFC_GET_SIMPLE_FORMAT'	: 0x1021,
	'SFC_SET_CLIPPING'	: 0x10C0,
	'SFC_GET_EMBED_FILE_INFO'	: 0x10B0,
	'SFC_GET_BROADCAST_INFO'	: 0x10F0,
	'SFC_GET_NORM_DOUBLE'	: 0x1010
}

SF_ERRORS = {
	'SF_ERR_UNRECOGNISED_FORMAT'	: 1,
	'SF_ERR_NO_ERROR'	: 0,
	'SF_ERR_SYSTEM'	: 2,
	'SF_ERR_UNSUPPORTED_ENCODING'	: 4,
	'SF_ERR_MALFORMED_FILE'	: 3
}

# format equivalence: dic used to create internally
# the right enum values from user friendly strings
py_to_snd_encoding_dic    = {
    'pcms8' : SF_FORMAT['SF_FORMAT_PCM_S8'],      
    'pcm16' : SF_FORMAT['SF_FORMAT_PCM_16'],     
    'pcm24' : SF_FORMAT['SF_FORMAT_PCM_24'],    
    'pcm32' : SF_FORMAT['SF_FORMAT_PCM_32'],    

    'pcmu8' : SF_FORMAT['SF_FORMAT_PCM_U8'],  

    'float32' : SF_FORMAT['SF_FORMAT_FLOAT'],
    'float64' : SF_FORMAT['SF_FORMAT_DOUBLE'],

    'ulaw'      : SF_FORMAT['SF_FORMAT_ULAW'],
    'alaw'      : SF_FORMAT['SF_FORMAT_ALAW'],
    'ima_adpcm' : SF_FORMAT['SF_FORMAT_IMA_ADPCM'],
    'ms_adpcm'  : SF_FORMAT['SF_FORMAT_MS_ADPCM'],

    'gsm610'    : SF_FORMAT['SF_FORMAT_GSM610'],
    'vox_adpcm' : SF_FORMAT['SF_FORMAT_VOX_ADPCM'],

    'g721_32'   : SF_FORMAT['SF_FORMAT_G721_32'], 
    'g723_24'   : SF_FORMAT['SF_FORMAT_G723_24'],
    'g723_40'   : SF_FORMAT['SF_FORMAT_G723_40'],

    'dww12' : SF_FORMAT['SF_FORMAT_DWVW_12'],
    'dww16' : SF_FORMAT['SF_FORMAT_DWVW_16'],
    'dww24' : SF_FORMAT['SF_FORMAT_DWVW_24'],
    'dwwN'  : SF_FORMAT['SF_FORMAT_DWVW_N'],

    'dpcm8' : SF_FORMAT['SF_FORMAT_DPCM_8'],
    'dpcm16': SF_FORMAT['SF_FORMAT_DPCM_16']
}

py_to_snd_file_format_dic = {
    'wav'   : SF_FORMAT['SF_FORMAT_WAV'],
    'aiff'  : SF_FORMAT['SF_FORMAT_AIFF'],
    'au'    : SF_FORMAT['SF_FORMAT_AU'],
    'raw'   : SF_FORMAT['SF_FORMAT_RAW'],
    'paf'   : SF_FORMAT['SF_FORMAT_PAF'],
    'svx'   : SF_FORMAT['SF_FORMAT_SVX'],
    'nist'  : SF_FORMAT['SF_FORMAT_NIST'],
    'voc'   : SF_FORMAT['SF_FORMAT_VOC'],
    'ircam' : SF_FORMAT['SF_FORMAT_IRCAM'],
    'wav64' : SF_FORMAT['SF_FORMAT_W64'],
    'mat4'  : SF_FORMAT['SF_FORMAT_MAT4'],
    'mat5'  : SF_FORMAT['SF_FORMAT_MAT5'],
    'pvf'   : SF_FORMAT['SF_FORMAT_PVF'],
    'xi'    : SF_FORMAT['SF_FORMAT_XI'],
    'htk'   : SF_FORMAT['SF_FORMAT_HTK'],
    'sds'   : SF_FORMAT['SF_FORMAT_SDS'],
    'avr'   : SF_FORMAT['SF_FORMAT_AVR'],
    'wavex' : SF_FORMAT['SF_FORMAT_WAVEX'],
    'sd2'   : SF_FORMAT['SF_FORMAT_SD2'],
    'flac'  : SF_FORMAT['SF_FORMAT_FLAC'],
    'caf'   : SF_FORMAT['SF_FORMAT_CAF']
}

py_to_snd_endianness_dic = {
    'file'      : SF_ENDIAN['SF_ENDIAN_FILE'], 
    'little'    : SF_ENDIAN['SF_ENDIAN_LITTLE'], 
    'big'       : SF_ENDIAN['SF_ENDIAN_BIG'], 
    'cpu'       : SF_ENDIAN['SF_ENDIAN_CPU']
}

# Those following dic are used internally to get user-friendly values from
# sndfile enum
SND_TO_PY_ENCODING = \
        dict([(i, j) for j, i in py_to_snd_encoding_dic.items()])
SND_TO_PY_FILE_FORMAT = \
        dict([(i, j) for j, i in py_to_snd_file_format_dic.items()])
SND_TO_PY_ENDIANNESS = \
        dict([(i, j) for j, i in py_to_snd_endianness_dic.items()])

#==========================================
# Check that libsndfile is expected version
#==========================================
def get_libsndfile_version():
    nverbuff = 256
    verbuff = create_string_buffer(nverbuff)
    n = _SND.sf_command(c_int(0), c_int(SF_COMMAND['SFC_GET_LIB_VERSION']), 
            verbuff, nverbuff)
    if n < 1:
        raise Exception("Error while getting version of libsndfile")

    # Transform the buffer into a string
    ver = ""
    for i in range(n):
        ver += verbuff[i]

    # Get major, minor and micro from version
    version     = ver.split('-')[1]
    prerelease  = 0
    major, minor, micro = [i for i in version.split('.')]
    try:
        micro   = int(micro)
    except ValueError,e:
        print "micro is "  + str(micro) 
        micro, prerelease   = micro.split('pre')

    return int(major), int(minor), int(micro), prerelease

MAJOR, MINOR, MICRO, PRERELEASE = get_libsndfile_version()
if not(MAJOR == 1):
    raise Exception("audiolab expects major version %d of libsndfile" % 1)
if MICRO > 25:
    if PRERELEASE == 0: 
        prestr  = "No"
    else:
        prestr  = "%s" % PRERELEASE
    print "WARNING libsndfile-%d.%d.%d (prerelease: %s) "\
        "this has only been tested with libsndfile 1.0.17 for now, "\
        "use at your own risk !" % (MAJOR, MINOR, MICRO, prestr)

#================
# Python wrappers
#================

#+++++++++++++++++
# Public exception
#+++++++++++++++++
class PyaudioException(Exception):
    pass

class InvalidFormat(PyaudioException):
    pass

class PyaudioIOError(PyaudioException, IOError):
    pass

class WrappingError(PyaudioException):
    pass

class FlacUnsupported(RuntimeError, PyaudioException):
    pass

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Private classes/function (Should not be used outside this file)
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
class _sf_info(Structure):
    """Structure representing C structure SF_INFO"""
    _fields_    = [('frames', c_int64),
                ('samplerate', c_int),
                ('channels', c_int),
                ('format', c_int),
                ('sections', c_int),
                ('seekable', c_int)]
    def __str__(self):
        return "%d frames, sr = %d Hz, %d channels, format is %d" % \
                (self.frames, self.samplerate, self.channels, self.format)

class _sf_format_info(Structure):
    """Structure representing C structure SF_FORMAT_INFO (useful for
    sf_command )"""
    _fields_    = [('format', c_int),
                ('name', c_char_p),
                ('extension', c_char_p)]
    def __str__(self):
        return "format hex is %#010x, name is %s, extension is %s" %  \
                (self.format, self.name, self.extension)

    def __repr__(self):
        print self.__str__()

class _sndfile(Structure):
    pass

sf_info_p = POINTER(_sf_info)
sndfile_p = POINTER(_sndfile)

# functions args
# TODO: is there a way to ensure that arg1 is the right kind of pointer ?
arg1    = c_char_p
arg2    = c_int
arg3    = sf_info_p
_SND.sf_open.argtypes   = [arg1, arg2, arg3]
_SND.sf_open.restype    = sndfile_p

arg1    = sndfile_p
_SND.sf_close.argtypes  = [arg1]
_SND.sf_close.restype  = c_int

arg1    = c_int
arg2    = c_int
arg3    = sf_info_p
arg4    = c_int
_SND.sf_open_fd.argtypes   = [arg1, arg2, arg3, arg4]
_SND.sf_open_fd.restype    = sndfile_p

arg1    = sndfile_p
arg2    = ndpointer(dtype=N.float64)
arg3    = c_int64

# double function
_SND.sf_readf_double.argtypes    = [arg1, arg2, arg3]
_SND.sf_readf_double.restype     = c_int64

_SND.sf_writef_double.argtypes    = [arg1, arg2, arg3]
_SND.sf_writef_double.restype     = c_int64

# float function
arg1    = sndfile_p
arg2    = ndpointer(dtype=N.float32)
arg3    = c_int64
_SND.sf_readf_float.argtypes    = [arg1, arg2, arg3]
_SND.sf_readf_float.restype     = c_int64

_SND.sf_writef_float.argtypes    = [arg1, arg2, arg3]
_SND.sf_writef_float.restype     = c_int64

# int function
arg1    = sndfile_p
arg2    = ndpointer(dtype=N.int32)
arg3    = c_int64
_SND.sf_readf_int.argtypes    = [arg1, arg2, arg3]
_SND.sf_readf_int.restype     = c_int64

_SND.sf_writef_int.argtypes    = [arg1, arg2, arg3]
_SND.sf_writef_int.restype     = c_int64

# short function
arg1    = sndfile_p
arg2    = ndpointer(dtype=N.int16)
arg3    = c_int64
_SND.sf_readf_short.argtypes    = [arg1, arg2, arg3]
_SND.sf_readf_short.restype     = c_int64

_SND.sf_writef_short.argtypes    = [arg1, arg2, arg3]
_SND.sf_writef_short.restype     = c_int64

# Error functions
arg1    = sndfile_p
_SND.sf_strerror.argtypes   = [arg1]
_SND.sf_strerror.restype    = c_char_p

# Function to sync data to file
arg1    = sndfile_p
_SND.sf_write_sync.argtypes = [arg1]

# Function to seek
arg1    = sndfile_p
arg2    = c_int64
arg3    = c_int
_SND.sf_seek.argtypes = [arg1, arg2, arg3]
_SND.sf_seek.restype  = c_int64

# To pass when a C function needs a NULL arg
_cNULL = POINTER(c_int)()

class _format_from_internal:
    """Class to handle audio format with sndfile. 
    
    DO NOT USE THIS CLASS OUTSIDE pysndfile.py MODULE: YOU MAY CRASH YOUR
    INTERPRETER !
    
    Basically, we have 3 classes of parameters:
        - the main format: (major format), like wav, aiff, etc...
        - the subtype format: pcm, bits resolution
        - endianness: little, big, as the cpu, default of the format

    This class encapsulates those parameters, and can build a representation of
    them from the format integer of sf_info. This should *NOT* be used, use
    format instead, which inherits this class to build a valid format from user
    friendly arguments.  """
    def __init__(self, format_integer):
        # Get the internal values which corresponds to the values libsndfile
        # can understand
        self._int_type = format_integer & SF_FORMAT['SF_FORMAT_TYPEMASK']
        self._int_encoding = format_integer & SF_FORMAT['SF_FORMAT_SUBMASK']
        self._int_endianness = format_integer & SF_FORMAT['SF_FORMAT_ENDMASK']

        assert format_integer == self._int_type | self._int_encoding |\
            self._int_endianness
        self._format    = format_integer

        # Now, we need to test if the combination of format, encoding and 
        # endianness is valid. sf_format_check needs also samplerate and
        # channel information, so just give a fake samplerate and channel
        # number. Looking at sndfile.c, it looks like samplerate is never
        # actually checked, and that when channels is checked, it is only
        # checked against values different than 1 or 2, so giving a value of
        # 1 to channel should be ok.
        self._sfinfo            = _sf_info()
        self._sfinfo.channels   = 1
        self._sfinfo.samplerate = 8000
        self._sfinfo.format     = self._format

        ret = _SND.sf_format_check(pointer(self._sfinfo))
        if ret is not SF_BOOL['SF_TRUE']:
            raise InvalidFormat()

        # Get the sndfile string description of the format type
        blop = _sf_format_info()
        blop.format = self._int_type
        st = _SND.sf_command(_cNULL, SF_COMMAND['SFC_GET_FORMAT_INFO'], \
                pointer(blop), sizeof(blop))
        if st is not 0:
            if SND_TO_PY_FILE_FORMAT[self._int_type] == 'flac':
                raise FlacUnsupported("Flac is not supported by your version"\
                        " of libsndfile")
            else:
                raise WrappingError("Could not get format string for format "\
                        "%d, " % blop.format + "please report this problem "\
                        "to the maintainer")
                    
        self.format_str = blop.name

        # Get the sndfile string description of the format subtype
        blop.format = self._int_encoding
        st = _SND.sf_command(_cNULL, SF_COMMAND['SFC_GET_FORMAT_INFO'], \
                pointer(blop), sizeof(blop))
        if st is not 0:
            raise WrappingError()
                    
        self.encoding_str   = blop.name

    def get_format_raw(self):
        """Do not use this function !"""
        return self._format

    def get_major_str(self):
        """Do not use this function !"""
        return self.format_str

    def get_encoding_str(self):
        """Do not use this function !"""
        return self.encoding_str

    def get_file_format(self):
        """return user friendly file format string"""
        return SND_TO_PY_FILE_FORMAT[self._int_type]

    def get_encoding(self):
        """return user friendly encoding string"""
        return SND_TO_PY_ENCODING[self._int_encoding]

    def get_endianness(self):
        """return user friendly file format string"""
        return SND_TO_PY_ENDIANNESS[self._int_endianness]

    # Various function
    def is_type(self, t):
        return (self._format & SF_FORMAT['SF_FORMAT_TYPEMASK']) \
                == py_to_snd_file_format_dic[t]

    # Syntactic sugar
    def __str__(self):
        return  "Major Format: %s, Encoding Format: %s" % \
                (self.format_str, self.encoding_str)

    def __repr__(self):
        return self.__str__()

#+++++++++++
# Public API
#+++++++++++

class formatinfo(_format_from_internal):
    def __init__(self, type = 'wav', encoding = 'pcm16', endianness = 'file'):
        """Build a valid format usable by the sndfile class when opening an
        audio file for writing. 
        
        Blah blah

        :Parameters:
            type : string
                represents the major file format (wav, etc...).
            encoding : string
                represents the encoding (pcm16, etc..).
            endianness : string
                represents the endianess.
            
        Notes
        -----
        
        Valid type strings are listed by file_format_dic.keys() Valid encoding
        strings are listed by encoding_dic.keys() Valid endianness strings are
        listed by endianness_dic.keys() """
        # Keep the arguments
        self.type       = type
        self.encoding   = encoding
        self.endianness = endianness

        # Get the internal values which corresponds to the values libsndfile
        # can understand
        self._int_type          = py_to_snd_file_format_dic[type]
        self._int_encoding      = py_to_snd_encoding_dic[encoding]
        self._int_endianness    = py_to_snd_endianness_dic[endianness]

        # Build the internal integer from parameters, and pass it to the super
        # class, which will do all the work
        format  = self._int_type | self._int_encoding | self._int_endianness

        _format_from_internal.__init__(self, format)

class sndfile:
    """Main class to open, read and write audio files"""
    def __init__(self, filename, mode = 'read', format = None, channels = 0, \
            samplerate = 0):
        """Create an instance of sndfile.

        :Parameters:
            filename : string or int
                name of the file to open (string), or file descriptor (integer)
            mode : string
                'read' for read, 'write' for write, or 'rwrite' for read and
                write.
            format : formatinfo
                when opening a new file for writing, give the format to write
                in.
            channels : int
                number of channels.
            samplerate : int
                sampling rate.

        :Returns:
            sndfile: a valid sndfile object 
            
        Notes
        -----
        
        format, channels and samplerate need to be given only in the write
        modes and for raw files.  """
        # Check the mode is one of the expected values
        if mode == 'read':
            sfmode  = SFM['SFM_READ']
        elif mode == 'write':
            sfmode  = SFM['SFM_WRITE']
            if format == None:
                raise Exception("For write mode, you should provide"\
                        "a format argument !")
        elif mode == 'rwrite':
            sfmode  = SFM['SFM_RDWR']
            if format == None:
                raise Exception("For write mode, you should provide"\
                        "a format argument !")
        else:
            raise Exception("mode %s not recognized" % str(mode))

        sfinfo = _sf_info()
        sfinfo_p = pointer(sfinfo)

        # Fill the sfinfo struct
        sfinfo.frames       = c_int64(0)
        if type(channels) is not int:
            print "Warning, channels is converted to int, was %s" % \
                    str(type(channels))
            sfinfo.channels     = int(channels)
        else:
            sfinfo.channels     = channels

        if type(samplerate) is not int:
            print "Warning, sampling rate is converted to int, was %s" % \
                    str(type(samplerate))
            sfinfo.samplerate   = int(samplerate)
        else:
            sfinfo.samplerate   = samplerate

        sfinfo.sections     = 0
        sfinfo.seekable     = False
        if mode == 'read' and format == None:
            sfinfo.format   = 0
        else:
            if sfinfo.channels > 256 or sfinfo.channels < 1:
                msg = "number of channels is %d, expected " \
                        "between 1 and 256" % sfinfo.channels
                raise RuntimeError(msg)
            sfinfo.format   = format.get_format_raw()
            if not _SND.sf_format_check(sfinfo_p):
                msg = "unknown error in format specification ?" +\
                        " Please report this to the author"
                raise WrappingError()

        sfinfo_p = pointer(sfinfo)
        self._sfmode = sfmode
        self.hdl = 0

        if type(filename) == int:
            res = _SND.sf_open_fd(filename, self._sfmode, sfinfo_p, 
                                  SF_BOOL['SF_FALSE'])
            self._byfd = True
            self.fd = filename
            self.filename = ""
        else:
            res = _SND.sf_open(filename, self._sfmode, sfinfo_p)
            self._byfd = False
            self.filename = filename

        try:
            # If res is NULL, this statement will raise a ValueError exception
            a = res[0]
        except ValueError:
            if self._byfd:
                msg = "error while opening file descriptor %d\n\t->" % self.fd
            else:
                msg = "error while opening file %s\n\t-> " % self.filename
            msg += _SND.sf_strerror(res)
            if self._byfd:
                msg += """
(Check that the mode argument passed to sndfile is the same than the one used
when getting the file descriptor, eg do not pass 'read' to sndfile if you
passed 'write' to open to get the file descriptor. If you are on win32, you are
out of luck, because its implementation of POSIX open is broken)"""
            raise IOError("error while opening %s\n\t->%s" % (filename, msg))

        if mode == 'read':
            tmp = _format_from_internal(sfinfo.format)
            self._format = formatinfo(tmp.get_file_format(), \
                    tmp.get_encoding(), tmp.get_endianness())
        else:
            self._format     = format

        self._sfinfo    = sfinfo
        self.hdl        = res

        if self.get_file_format() == 'flac':
            def SeekNotEnabled(self, *args):
                raise FlacUnsupported("seek not supported on Flac by default,"\
                        " because\n some version of FLAC libraries are buggy."\
                        " Read FLAC_SUPPORT.txt")
            self.seek   = SeekNotEnabled 
        else:
            self.seek = self._seek

    def __del__(self, close_func = _SND.sf_close):
        # Stupid python needs the close_func, otherwise
        # it may clean ctypes before calling here
        if hasattr(self,'hdl'):
            if not(self.hdl == 0):
                close_func(self.hdl)
                self.hdl    = 0

    def close(self):
        """close the file."""
        self.__del__()

    def sync(self):
        """call the operating system's function to force the writing of all
        file cache buffers to disk the file. 
        
        No effect if file is open as read"""
        _SND.sf_write_sync(self.hdl)

    def _seek(self, offset, whence = 0, mode = 'rw'):
        """similar to python seek function, taking only in account audio data.
        
        :Parameters:
            offset : int
                the number of frames (eg two samples for stereo files) to move
                relatively to position set by whence.
            whence : int
                only 0 (beginning), 1 (current) and 2 (end of the file) are
                valid.
            mode : string
                If set to 'rw', both read and write pointers are updated. If
                'r' is given, only read pointer is updated, if 'w', only the
                write one is (this may of course make sense only if you open
                the file in a certain mode).

        Notes
        -----
        
        - one only takes into accound audio data. 
        - if an invalid seek is given (beyond or before the file), a
          PyaudioIOError is launched."""
        c_offset    = _num2int64(offset)
        if mode == 'rw':
            # Update both read and write pointers
            st  = _SND.sf_seek(self.hdl, c_offset, whence)
        elif mode == 'r':
            whence = whence | SFM['SFM_READ']
            st  = _SND.sf_seek(self.hdl, c_offset, whence)
        elif mode == 'w':
            whence = whence | SFM['SFM_WRITE']
            st  = _SND.sf_seek(self.hdl, c_offset, whence)
        else:
            raise ValueError("mode should be one of 'r', 'w' or 'rw' only")

        if st == -1:
            msg = "Error while seeking, libsndfile error is %s" \
                    % (_SND.sf_strerror(self.hdl))
            raise PyaudioIOError(msg)
        return st

    # Functions to get informations about the file
    def get_nframes(self):
        """ Return the number of frames of the file"""
        if self._sfmode == SFM['SFM_READ']:
            # XXX: is this reliable for any file (think pipe and co ?)
            return self._sfinfo.frames
        else:
            # In write/rwrite mode, the only reliable way to get the number of
            # frames is to use seek.
            raise NotImplementedError("Sorry, getting the current number of"
                    "frames in write modes is not supported yet")
    
    def get_samplerate(self):
        """ Return the samplerate in Hz of the file"""
        return self._sfinfo.samplerate
    
    def get_channels(self):
        """ Return the number of channels of the file"""
        return self._sfinfo.channels
    
    def get_file_format(self):
        """return user friendly file format string"""
        return SND_TO_PY_FILE_FORMAT[self._format._int_type]

    def get_encoding(self):
        """return user friendly encoding string"""
        return SND_TO_PY_ENCODING[self._format._int_encoding]

    def get_endianness(self):
        """return user friendly file format string"""
        return SND_TO_PY_ENDIANNESS[self._format._int_endianness]

    #------------------
    # Functions to read
    #------------------
    def read_frames(self, nframes, dtype = N.float64):
        """Read nframes frames of the file.
        
        :Parameters:
            nframes : int
                number of frames to read.
            dtype : numpy dtype
                dtype of the returned array containing read data (see note).
        
        Notes
        -----
        
        - read_frames updates the read pointer.
        - One column is one channel.
        - if float are requested when the file contains integer data, you will
          get normalized data (that is the max possible integer will be 1.0,
          and the minimal possible value -1.0).
        - if integers are requested when the file contains floating point data,
          it may give wrong results because there is an ambiguity: if the
          floating data are normalized, you can get a file with only 0 !
          Getting integer data from files encoded in normalized floating point
          is not supported (yet: sndfile supports it).""" 
        c_nframes   = _num2int64(nframes)
        if c_nframes < 0:
            raise ValueError("number of frames has to be >= 0")

        # XXX: inout argument
        if self._sfinfo.channels > 1:
            y           = N.zeros((nframes, self._sfinfo.channels), dtype)
        else:
            y           = N.zeros(nframes, dtype)

        if dtype == N.float64:
            res         = _SND.sf_readf_double(self.hdl, y, c_nframes)
        elif dtype == N.float32:
            res         = _SND.sf_readf_float(self.hdl, y, c_nframes)
        elif dtype == N.int32:
            res         = _SND.sf_readf_int(self.hdl, y, c_nframes)
        elif dtype == N.int16:
            res         = _SND.sf_readf_short(self.hdl, y, c_nframes)
        else:
            raise RuntimeError("Sorry, only float, double, int and short "
                               "read supported for now")

        if not(res == nframes):
            y = y[0:res]

        return y

    #-------------------
    # Functions to write
    #-------------------
    # TODO: Think about overflow vs type of input, etc...
    def write_frames(self, input, nframes = -1):
        """write data to file.
        
        :Parameters:
            input : ndarray
                array containing data to write.  
            nframes : int
                number of frames to write.

        Notes
        -----

        - one channel is one column
        - updates the write pointer.
        - if float are given when the file contains integer data, you should
          put normalized data (that is the range [-1..1] will be written as the
          maximum range allowed by the integer bitwidth)."""
        # First, get the number of channels and frames from input
        if input.ndim   == 1:
            nc      = 1
        else:
            if input.ndim > 2:
                raise Exception("Expect array of rank <= 2, got %d" \
                        % input.ndim)
            nc = input.shape[1]

        if nframes == -1:
            nframes = N.size(input) / nc
        # Number of channels should be the one expected
        if not(nc == self._sfinfo.channels):
            raise Exception("Expected %d channels, got %d" % \
                    (self._sfinfo.channels, nc))

        # Writing to the file
        c_nframes   = _num2int64(nframes)
        if c_nframes < 0:
            raise ValueError("number of frames has to be >= 0")

        input = N.require(input, requirements = 'C')

        if input.dtype == N.float32:
            if self._check_overflow(input):
                warnings.warn("Warning, overflow detected when writing.")
            res         = _SND.sf_writef_float(self.hdl, input, c_nframes)
        elif input.dtype == N.float64:
            self._check_overflow(input)
            if self._check_overflow(input):
                warnings.warn("Warning, overflow detected when writing.")
            res         = _SND.sf_writef_double(self.hdl, input, c_nframes)
        elif input.dtype == N.int32:
            res         = _SND.sf_writef_int(self.hdl, input, c_nframes)
        elif input.dtype == N.int16:
            res         = _SND.sf_writef_short(self.hdl, input, c_nframes)
        else:
            raise Exception("type of input not understood: input should"
                " be float64 or float32""")

        if not(res == nframes):
            raise IOError("write %d frames, expected to write %d" \
                    % res, nframes)

    def _check_overflow(self, data):
        if N.max(data ** 2) >= 1.:
            return True
        return False

    # Syntactic sugar
    def __repr__(self):
        return self.__str__()

    def __str__(self):
        repstr = "----------------------------------------\n"
        if self._byfd:
            repstr  += "File        : %d (opened by file descriptor)\n" % self.fd
        else:
            repstr  += "File        : %s\n" % self.filename
        repstr  += "Channels    : %d\n" % self._sfinfo.channels
        repstr  += "Sample rate : %d\n" % self._sfinfo.samplerate
        repstr  += "Frames      : %d\n" % self._sfinfo.frames
        repstr  += "Raw Format  : %#010x -> %s\n" % \
                (self._format.get_format_raw(), self._format.get_major_str())
        repstr  += "File format : %s\n" % self.get_file_format()
        repstr  += "Encoding    : %s\n" % self.get_encoding()
        repstr  += "Endianness  : %s\n" % self.get_endianness()
        repstr  += "Sections    : %d\n" % self._sfinfo.sections
        if self._sfinfo.seekable:
            seek    = 'True'
        else:
            seek    = 'False'
        repstr  += "Seekable    : %s\n" % seek
        repstr  += "Duration    : %s\n" % self._generate_duration_str()
        return repstr

    def _generate_duration_str(self):
        if self._sfinfo.samplerate < 1:
            return None
        tsec    = self._sfinfo.frames / self._sfinfo.samplerate
        hrs     = tsec / 60 / 60
        tsec    = tsec % (60 ** 2)
        mins    = tsec / 60
        tsec    = tsec % 60
        secs    = tsec
        ms      = 1000 * self._sfinfo.frames / self._sfinfo.samplerate % 1000

        return "%02d:%02d:%02d.%3d" % (hrs, mins, secs, ms)

def supported_format():
    # XXX: broken
    return py_to_snd_file_format_dic.keys()

def supported_endianness():
    # XXX: broken
    return py_to_snd_endianness_dic.keys()

def supported_encoding():
    # XXX: broken
    return py_to_snd_encoding_dic.keys()

def _num2int64(value):
    """ Convert a python objet to a c_int64, safely."""
    if not (type(value) == int or type(value) == long):
        value = long(value)
        print "Warning, converting %s to long" % str(value)
    c_value = c_int64(value)
    if not c_value.value == value:
        raise RuntimeError("Error while converting %s to a c_int64"\
            ", maybe %s is too big ?" % str(value))
    return c_value
