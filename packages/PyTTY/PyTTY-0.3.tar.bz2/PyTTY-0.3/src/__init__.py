# -*- coding: utf-8 -*-

'''Python serial access package

    This package provides easy access to TTY devices from Python.
'''

__credits__ = '''Copyright (C) 2010,2011 Arc Riley

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU Lesser General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public License
    along with this program; if not, see http://www.gnu.org/licenses
'''

__author__  = '\n'.join((
  'Arc Riley <arcriley@gmail.com>',
  'Chris Koepke',
))

__version__ = '0.3'


import io


class TTY (io.BufferedRWPair) :
    '''TTY io class

    This is a subclass of io.BufferedRWPair from the Python standard library
    which opens a tty device, sets nonblock mode on the device, and allows the
    user to change baud rate, flow control, and other settings often available
    to tty devices.

        >>> import os
        >>> ptys = os.openpty()  # create two connected ptys for testing
        >>> master = pytty.TTY(ptys[0])
        >>> slave = pytty.TTY(ptys[1])
        >>> slave.write('Greetings, Master.'.encode()) == 18
        True
        >>> slave.flush()
        >>> print(master.read().decode())
        Greetings, Master.
    '''

    # This is intended to be overridden by some subclasses
    _iobase = io.FileIO


    def __init__ (self, name) :
        from fcntl import fcntl, F_SETFL, F_GETFL
        from os import O_NONBLOCK

        reader = self._iobase(name, 'r')

        # ensure this is actually a tty device
        if not reader.isatty() :
            raise IOError('%s is not a tty device' % name)

        # set non-blocking mode on the reader
        self._fdo = reader.fileno()
        fcntl(self._fdo, F_SETFL, (fcntl(self._fdo, F_GETFL) | O_NONBLOCK))

        # open a separate writer device
        writer = self._iobase(name, 'w')

        # set non-blocking mode on the reader
        self._fdi = reader.fileno()
        fcntl(self._fdi, F_SETFL, (fcntl(self._fdi, F_GETFL) | O_NONBLOCK))

        # initialize self with BufferedRWPair
        super(TTY, self).__init__(reader, writer)


    @property
    def baud (self) :
        '''Baud rate

    Value must be supported by the tty device and in this list::

        [0, 50, 75, 110, 134, 150, 200, 300, 600, 1200, 1800, 2400, 4800,
        9600, 19200, 38400, 57600, 115200, 230400, 460800]
        '''
        import termios
        return {
            termios.B0 : 0,           termios.B50 : 50,
            termios.B75 : 75,         termios.B110 : 110,
            termios.B134 : 134,       termios.B150 : 150,
            termios.B200 : 200,       termios.B300 : 300,
            termios.B600 : 600,       termios.B1200 : 1200,
            termios.B1800 : 1800,     termios.B2400 : 2400,
            termios.B4800 : 4800,     termios.B9600 : 9600,
            termios.B19200 : 19200,   termios.B38400 : 38400,
            termios.B57600 : 57600,   termios.B115200 : 115200,
            termios.B230400 : 230400, termios.B460800 : 460800,
        }[termios.tcgetattr(self._fdi)[4]]


    @baud.setter
    def baud (self, value) :
        import termios
        try :
            tv = {
                0 : termios.B0,           50 : termios.B50,
                75 : termios.B75,         110 : termios.B110,
                134 : termios.B134,       150 : termios.B150,
                200 : termios.B200,       300 : termios.B300,
                600 : termios.B600,       1200 : termios.B1200,
                1800 : termios.B1800,     2400 : termios.B2400,
                4800 : termios.B4800,     9600 : termios.B9600,
                19200 : termios.B19200,   38400 : termios.B38400,
                57600 : termios.B57600,   115200 : termios.B115200,
                230400 : termios.B230400, 460800 : termios.B460800,
            }[value]
        except KeyError :
            raise IOError('Baud rate not supported by PyTTY.')
        tci = termios.tcgetattr(self._fdi)
        tco = termios.tcgetattr(self._fdo)
        tci[4], tci[5], tco[4], tco[5] = (tv,)*4
        termios.tcsetattr(self._fdi, termios.TCSANOW, tci)
        termios.tcsetattr(self._fdo, termios.TCSANOW, tco)


# Clean up package namespace
del(io)

