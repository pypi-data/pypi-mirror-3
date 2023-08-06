# -*- coding: utf-8 -*-
#!/usr/bin/env python
#   Copyright (C) 2012 Samuele Carcagno <sam.carcagno@gmail.com>
#   This file is part of pybdf

#    pybdf is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    pybdf is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with pybdf.  If not, see <http://www.gnu.org/licenses/>.

"""
This module can be used to read the header and data from
24-bit BIOSEMI BDF files recorded with the ActiveTwo system.

 Examples
 --------
 >>> bdf_rec = bdfRecording('res1.bdf') #create bdfRecording object
 >>> bdf_rec.recordDuration #how many seconds the recording lasts
 >>> bdf_rec.sampRate #sampling rate for each channel
 >>> #read 10 seconds of data from the first two channels
 >>> rec = bdf_rec.get_data(channels=[0, 1], beginning=0, end=10)
 >>> rec = bdf_rec.get_data_parallel() #read all data using multiprocess
"""
import copy, multiprocessing, numpy
from numpy import where, diff
__version__ = 0.1

class bdfRecording:
    """
    Class for dealing with BIOSEMI 24-bit BDF files.
    A bdfRecording object is created with the following syntax::
        >>> bdf_rec = bdfRecording('bdf_file.bdf')
    This reads the BDF header, but not the data. You need to use
    the get_data() or get_data_parallel() methods to read the data.
    The full documentation of the BDF file format can be found here:
    http://www.biosemi.com/faq/file_format.htm

    Attributes
    ----------
    idCode : str
        Identification code
    subjId : str
        Local subject identification
    recId : str
        Local recording identification
    startDate : str
        Recording start date
    startTime : str
        Recording start time
    nBytes : int
        Number of bytes occupied by the bdf header
    versionDataFormat : str
        Version of data format
    nDataRecords : int
        Number of data records "-1" if unknown
    recordDuration : float
        Duration of a data record, in seconds
    nChannels : int
        Number of channels in data record
    chanLabels : list of str
        Channel labels
    transducer : list of str
        Transducer type
    physDim : str
        Physical dimension of channels
    physMin : list of int
        Physical minimum in units of physical dimension
    physMax : list of int
        Physical maximum in units of physical dimension
    digMin : list of int
        Digital minimum
    digMax : list of int
        Digital maximum
    prefilt : list of str
        Prefiltering
    nSampRec : list of int
        Number of samples in each data record
    reserved : list of str
        Reserved
    scaleFactor : list of floats
        Scaling factor for digital to physical dimension
    sampRate : list of int
        Recording sampling rate
    statusChanIdx : int
        Index of the status channel
    nDataChannels : int
        Number of data channels containing data (rather than trigger codes)
    dataChanLabels : list of str
        Labels of the channels containing data (rather than trigger codes)
                                            
                                            
    """
    
    def __init__(self, fileName):
        self.fileName = fileName
        #try:
        f = open(self.fileName, "rb")
        #except IOError:
        #    print("Could not open file. Check that that the file name\
        #    is correct")
        #    return
        #python already throws an IOError if the file
        #does not exist, but maybe we should check that
        #the file is indeed of type BDF
        self.idCodeNonASCII = f.read(1)
        self.idCode = bytes.decode(f.read(7), 'ascii')
        self.subjId = bytes.decode(f.read(80), 'ascii')
        self.recId = bytes.decode(f.read(80), 'ascii')
        self.startDate = bytes.decode(f.read(8), 'ascii')
        self.startTime = bytes.decode(f.read(8), 'ascii')
        self.nBytes = int(bytes.decode(f.read(8), 'ascii'))
        self.versionDataFormat = bytes.decode(f.read(44), 'ascii')
        self.nDataRecords = int(bytes.decode(f.read(8), 'ascii'))
        self.recordDuration = float(bytes.decode(f.read(8), 'ascii').strip())
        self.nChannels = int(bytes.decode(f.read(4), 'ascii'))
        self.chanLabels = []
        self.transducer = []
        self.physDim = []
        self.physMin = []
        self.physMax = []
        self.digMin = []
        self.digMax = []
        self.prefilt = []
        self.nSampRec = []
        self.reserved = []
        self.scaleFactor = []
        self.sampRate = []
        
        self.duration = self.recordDuration * self.nDataRecords
        for i in range(self.nChannels):
            self.chanLabels.append(bytes.decode(f.read(16), 'ascii').strip())
        for i in range(self.nChannels):
            self.transducer.append(bytes.decode(f.read(80), 'ascii').strip())
        for i in range(self.nChannels):
            self.physDim.append(bytes.decode(f.read(8), 'ascii').strip())
        for i in range(self.nChannels):
            self.physMin.append(int(bytes.decode(f.read(8), 'ascii')))
        for i in range(self.nChannels):
            self.physMax.append(int(bytes.decode(f.read(8), 'ascii')))
        for i in range(self.nChannels):
            self.digMin.append(int(bytes.decode(f.read(8), 'ascii')))
        for i in range(self.nChannels):
            self.digMax.append(int(bytes.decode(f.read(8), 'ascii')))
        for i in range(self.nChannels):
            self.prefilt.append(bytes.decode(f.read(80), 'ascii').strip())
        for i in range(self.nChannels):
            self.nSampRec.append(int(bytes.decode(f.read(8), 'ascii')))
        for i in range(self.nChannels):
            self.reserved.append(bytes.decode(f.read(32), 'ascii'))
        for i in range(self.nChannels):
            self.scaleFactor.append((self.physMax[i] - self.physMin[i]) / (self.digMax[i] - self.digMin[i]))
        self.statusChanIdx = self.chanLabels.index("Status")
        self.nDataChannels = self.nChannels - 1
        self.dataChanLabels = copy.copy(self.chanLabels)
        self.dataChanLabels.pop()
        self.sampRate = list(numpy.array(numpy.round(numpy.array(self.nSampRec) / self.recordDuration), dtype=numpy.int16))
        f.close()
    def get_data(self, beginning=0, end=None, channels=None, trig=True, status=True, norm_trig=True, norm_status=True):

        """
        Read the data from a bdfRecording object

        Parameters
        ----------
        beginning : int
            Start time of data chunk to read (seconds).
        end : int
            End time of data chunk to read (seconds).
        channels : list of integers or strings
            Channels to read. Both channel numbers, or channel names are accepted. Note that channel numbers are indexed starting from *zero*.
        trig : boolean
            If True, return the channel containing the triggers
        status : boolean
            If True, return the channel containing the status codes
        norm_trig : boolean
            If True, the trigger channel will only signal *changes* between one trigger status to the next. A trigger value that is equal to the previous one will be set to zero
        norm_status : boolean
            If True, the status channel will only signal *changes* between one status code to the next. A code value that is equal to the previous one will be set to zero

        Returns
        -------
        rec : a dictionary with three keys
           - data : an array of floats with dimenions nChannels X nDataPoints
           - trigChan : an array of integers with the triggers in decimal format
           - statusChan : an array of integers with the status codes in decimal format
           - chanLabels : a list containing the labels of the channels that were read,
             in the same order they are inserted in the data matrix
        
        Examples
        --------
        >>> x = bdfRecording('res1.bdf')
        >>> rec = x.get_data(channels=[0, 2], beginning=0, end=10)
        """

        if end is None: #read all data
            end = self.nDataRecords
        if channels is None: #read all data channels
            channels = copy.copy(self.dataChanLabels)
        if len(channels) > self.nDataChannels:
            print("Requested channels more than available channels. Exiting")
            return
        for i in range(len(channels)): #if some or all channels were given as labels convert them to indexes
            if isinstance(channels[i], str):
                channels[i] = self.dataChanLabels.index(channels[i])
        channels = sorted(channels)
        chanLabels = []
        for i in range(len(channels)):
            chanLabels.append(self.dataChanLabels[channels[i]])
        nChannelsToRead = len(channels)
        
        f = open(self.fileName, "rb")
        recordsToRead = end - beginning
        data = numpy.zeros((nChannelsToRead, recordsToRead*self.nSampRec[0]))
        trigChan = numpy.zeros((recordsToRead*self.nSampRec[0]), dtype=numpy.int16) #just read them in, and in case user doesn't want them set to none later, skipping just slows things down because of loop
        statusChan = numpy.zeros((recordsToRead*self.nSampRec[0]), dtype=numpy.int16)
        i = 0
        f.seek(self.nBytes + beginning*self.nSampRec[0]*3*self.nChannels)
        for n in range(recordsToRead):
            for c in range(self.nChannels):
                if c != self.statusChanIdx:
                    if c in channels:
                        for s in range(self.nSampRec[c]):
                            currChanIdx = channels.index(c)
                            data[currChanIdx, n*self.nSampRec[c]+s] = int.from_bytes(f.read(3), byteorder='little', signed=True)
                    else:
                        currPos = f.tell()
                        f.seek(currPos + self.nSampRec[c]*3)
                else:
                    if trig == True or status == True:
                        for s in range(self.nSampRec[c]):
                            trigChan[n*self.nSampRec[c]+s] = int.from_bytes(f.read(2), byteorder='little', signed=True)
                            statusChan[n*self.nSampRec[c]+s] = int.from_bytes(f.read(1), byteorder='little', signed=True)
                    else:
                        currPos = f.tell()
                        f.seek(currPos + self.nSampRec[c]*3)
                              
        f.close()
        if trig == True:
            trigChan = 2**8 + trigChan
            if norm_trig == True:
                trigChan[where(diff(trigChan) == 0)[0]+1] = 0
        else:
            trigChan = None
        if status == True:
            statusChan = 2**8 + statusChan
            if norm_status == True:
                statusChan[where(diff(statusChan) == 0)[0]+1] = 0
        else:
            statusChan = None
        
        for c in range(nChannelsToRead):
            data[c,:] = data[c,:] * self.scaleFactor[c]

        rec = {}
        rec['data'] = data
        rec['trigChan'] = trigChan
        rec['statusChan'] = statusChan
        rec['chanLabels'] = chanLabels
        return rec

    def get_data_parallel(self, beginning=0, end=None, channels=None, trig=True, status=True, norm_trig=True, norm_status=True):
        """
        Read the data from a bdfRecording object using the multiprocessing
        module to exploit multicore machines.

        Parameters
        ----------
        beginning : int
            Start time of data chunk to read (seconds).
        end : int
            End time of data chunk to read (seconds).
        channels : list of integers or strings
            Channels to read. Both channel numbers, or channel names are accepted. Note that channel numbers are indexed starting from *zero*.
        trig : boolean
            If True, return the channel containing the triggers
        status : boolean
            If True, return the channel containing the status codes
        norm_trig : boolean
            If True, the trigger channel will only signal *changes* between one trigger status to the next. A trigger value that is equal to the previous one will be set to zero
        norm_status : boolean
            If True, the status channel will only signal *changes* between one status code to the next. A code value that is equal to the previous one will be set to zero

        Returns
        -------
        rec : a dictionary with three keys
           - data : an array of floats with dimenions nChannels X nDataPoints
           - trigChan : an array of integers with the triggers in decimal format
           - statusChan : an array of integers with the status codes in decimal format
           - chanLabels : a list containing the labels of the channels that were read,
             in the same order they are inserted in the data matrix
        Examples
        --------
        >>> x = bdfRecording('res1.bdf')
        >>> rec = x.get_data_parallel(channels=[0, 2], beginning=0, end=10)
        """

        trigChan = None #initialize to None in case user doesn't want them
        statusChan = None
        if end is None: #read all data
            end = self.nDataRecords
        if channels is None: #read all data channels
            channels = copy.copy(self.dataChanLabels)
        if len(channels) > self.nDataChannels:
            print("Requested channels more than available channels. Exiting")
            return
        for i in range(len(channels)):
            if isinstance(channels[i], str):
                channels[i] = self.dataChanLabels.index(channels[i])
        channels = sorted(channels)
        chanLabels = []
        for i in range(len(channels)):
            chanLabels.append(self.dataChanLabels[channels[i]])
        nChannelsToRead = len(channels)
        #chList = []
        pool = multiprocessing.Pool()
        if trig == True or status == True:
            nChanTot = nChannelsToRead+1
        else:
            nChanTot = nChannelsToRead
        res_li = [0 for i in range(nChanTot)]
            
        for i in range(nChannelsToRead):
            res_li[i] = pool.apply_async(readChannel, (self.fileName, channels[i], beginning, end, self.nChannels, self.nSampRec, self.scaleFactor, self.statusChanIdx, self.nBytes))
        if trig == True or status == True:
            res_li[i+1] = pool.apply_async(readChannel, (self.fileName, self.statusChanIdx, beginning, end, self.nChannels, self.nSampRec, self.scaleFactor, self.statusChanIdx, self.nBytes))
        pool.close()
        pool.join()
        
        
        for i in range(nChanTot):
            thisRes = res_li[i].get()
            if i == 0:
                data = numpy.zeros((nChannelsToRead, thisRes[1].shape[1]))
            if thisRes[0] == self.statusChanIdx:
                trigChan = thisRes[1][0,:]
                statusChan = thisRes[1][1,:]
            else:
                channelPos = thisRes[0]
                dataRow = channels.index(channelPos)
                data[dataRow,:] = thisRes[1]
        if trig == False:
            trigChan = None
        else:
            if norm_trig == True:
                trigChan[where(diff(trigChan) == 0)[0]+1] = 0
        if status == False:
            statusChan = None
        else:
            if norm_status == True:
                statusChan[where(diff(statusChan) == 0)[0]+1] = 0
        rec = {}
        rec['data'] = data
        rec['trigChan'] = trigChan
        rec['statusChan'] = statusChan
        rec['chanLabels'] = chanLabels
        return rec


def readChannel(fileName, channelNumber, beginning, end, nChannels, nSampRec, scaleFactor, statusChanIdx, nBytes):
    f = open(fileName, "rb")
    recordsToRead = end - beginning
    if channelNumber == statusChanIdx:
        data = numpy.zeros((2, recordsToRead*nSampRec[0]), dtype=numpy.int16)
    else:
        data = numpy.zeros((1, recordsToRead*nSampRec[0]))
    
    i = 0
    f.seek(nBytes + beginning*nSampRec[0]*3*nChannels)
    for n in range(recordsToRead):
        for c in range(nChannels):
            if c != statusChanIdx:
                if c == channelNumber:
                    for s in range(nSampRec[c]):
                        data[0, n*nSampRec[c]+s] = int.from_bytes(f.read(3), byteorder='little', signed=True)
                else:
                    currPos = f.tell()
                    f.seek(currPos + nSampRec[c]*3)
            else:
                if c == channelNumber:
                    for s in range(nSampRec[c]):
                        data[0, n*nSampRec[c]+s] = int.from_bytes(f.read(2), byteorder='little', signed=True)
                        data[1, n*nSampRec[c]+s] = int.from_bytes(f.read(1), byteorder='little', signed=True)
                else:
                    currPos = f.tell()
                    f.seek(currPos + nSampRec[c]*3)
    f.close()
    if channelNumber == statusChanIdx:
        data = 2**8 + data
    else:
        data = data * scaleFactor[channelNumber]
    dataL = [channelNumber, data]

    return dataL
