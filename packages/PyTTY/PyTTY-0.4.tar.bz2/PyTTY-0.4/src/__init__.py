# -*- coding: utf-8 -*-

'''Python serial access package

    This package provides easy access to TTY devices from Python.
'''

__credits__ = '''Copyright (C) 2010,2011,2012 Arc Riley

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

__version__ = '0.4'

import io

class TTY (io.BufferedRWPair) :
    '''TTY io class

    This is a subclass of io.BufferedRWPair from the Python standard library
    which opens a tty device, sets nonblock mode on the device, and allows the
    user to change baud rate, flow control, and other settings often available
    to tty devices.

        >>> import pty
        >>> ptys = pty.openpty()  # create two connected ptys for testing
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

    # Generator to compile our baudrate/integer lookup dicts
    def _baudrates() :
        import termios
        for member in termios.__dict__ :
            if member[0] == 'B' and member[1:].isdigit() :
                yield (int(member[1:]), termios.__dict__[member])

    # {termios.B9600 : 9600, termios.B19200 : 19200, etc}
    _baud2int = {b[1] : b[0] for b in _baudrates()}

    # {9600 : termios.B9600, 19200 : termios.B19200, etc}
    _int2baud = {b[0] : b[1] for b in _baudrates()}

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

    def __repr__(self) :
        return '<pytty.TTY (%s)>' % str(self)

    def __str__(self) :
        return '%s %i%s%i' % (self.baud, self.bits, self.parity, self.stops)

    @property
    def baud (self) :
        '''Baud rate

    Value must be supported by the tty device and the termios module.'''
        import termios
        try :
            return self._baud2int[termios.tcgetattr(self._fdi)[4]]
        except KeyError :
            raise IOError('Current baud rate not supported by termios.')

    @baud.setter
    def baud (self, value) :
        import termios
        try :
            tv = self._int2baud[value]
        except KeyError :
            raise IOError('Baud rate not supported by termios.')
        tci = termios.tcgetattr(self._fdi)
        tco = termios.tcgetattr(self._fdo)
        tci[4], tci[5], tco[4], tco[5] = (tv,)*4
        termios.tcsetattr(self._fdi, termios.TCSANOW, tci)
        termios.tcsetattr(self._fdo, termios.TCSANOW, tco)

    @property
    def bits (self) :
        '''Number of bits per byte

    This property determines how many bits are in a byte, between 5 and 8.
        '''
        import termios
        cflag = termios.tcgetattr(self._fdi)[2]
        return ((cflag & termios.CS8 and 8) or (cflag & termios.CS7 and 7) or
                (cflag & termios.CS6 and 6) or (cflag & termios.CS5 and 5))

    @bits.setter
    def bits (self, value) :
        import termios
        if value < 5 or value > 8 :
            raise IOError('Byte size must be between 5 and 8 bits.')
        cs = (termios.CS5, termios.CS6, termios.CS7, termios.CS8)[value-5]
        for fd in (self._fdi, self._fdo) :
            tc = termios.tcgetattr(fd)
            tc[2] &= cs
            termios.tcsetattr(fd, termios.TCSANOW, tc)

    @property
    def parity (self) :
        '''Parity bit

    This may be set to 'N' (none), 'E' (even), or 'O' (odd).
        '''
        import termios
        cflag = termios.tcgetattr(self._fdi)[2]
        return ((('N', 'N'), ('E', 'O'))
                [cflag & termios.PARENB and 1][cflag & termios.PARODD and 1])

    @parity.setter
    def parity (self, value) :
        import termios
        for fd in (self._fdi, self._fdo) :
            tc = termios.tcgetattr(fd)
            if value in 'Nn' :
                tc[2] &= ~termios.PARENB
            else :
                tc[2] |= termios.PARENB
                if value in 'Ee' :
                    tc[2] &= ~termios.PARODD
                elif value in 'Oo' :
                    tc[2] |= termios.PARODD
                else :
                    raise IOError("Parity must be 'N', 'E', or 'O'.")
            termios.tcsetattr(fd, termios.TCSANOW, tc)

    @property
    def stops (self) :
        '''Number of stop bits

    How many stop bits follow a byte, either 1 or 2.
        '''
        import termios
        cflag = termios.tcgetattr(self._fdi)[2]
        return (1, 2)[termios.tcgetattr(self._fdi)[2] & termios.CSTOPB and 1]

    @stops.setter
    def stops (self, value) :
        import termios
        for fd in (self._fdi, self._fdo) :
            tc = termios.tcgetattr(fd)
            if value == 1 :
                tc[2] &= ~termios.CSTOPB
            elif value == 2 :
                tc[2] &= termios.CSTOPB
            else :
                raise IOError('Stop bits must be either 1 or 2.')
            termios.tcsetattr(fd, termios.TCSANOW, tc)

# Clean up package namespace
del(io)
