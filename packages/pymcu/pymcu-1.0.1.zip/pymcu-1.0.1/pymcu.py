#!/usr/bin/env python 

# python interface for MicroControllers
# this is a wrapper module for the serial command interface
# between mcu and python.
#
# (C) 2011 Richard Wardlow
# this is distributed under a free software license, see license.txt
# http://www.pymcu.com


VERSION = '1.0.1'

import sys, os, serial, time


def mcuScan(baudrate=115200):
    """scan for available MCUs. return a dictionary (portname, index)"""
    available = {}
    if os.name == 'nt':
        for i in range(256):
            try:
                s = serial.Serial(i,baudrate,timeout=1)
                s.write('i' + chr(1) + chr(0))
                checkID = s.read(6)
                if 'pymcu' in checkID:
                    available[s.portstr] = i
                s.close()   # explicit close 'cause of delayed GC in java
            except serial.SerialException:
                pass
        return available
    if os.name == 'posix':
        for i in os.listdir('/dev/'):
            if 'ttyUSB' in i or 'usbserial' in i:
                try:
                    s = serial.Serial('/dev/' + i,baudrate,timeout=1)
                    s.write('i' + chr(1) + chr(0))
                    checkID = s.read(6)
                    if 'pymcu' in checkID:
                        available[s.portstr] = i
                    s.close()   # explicit close 'cause of delayed GC in java
                except serial.SerialException:
                    pass
        return available

class mcuModule:
    def __init__(self, port=None, baudrate=115200):
        self.active = False
        self.mcuType = None
        self.APins = [{'Min':1,'Max':6,'MinValue':0,'MaxValue':1023},{'Min':1,'Max':6,'MinValue':0,'MaxValue':1023}]
        self.DPins = [{'Min':1,'Max':13},{'Min':1,'Max':14}]
        self.PWMPins = [{'Min':1,'Max':5,'MinDuty':0,'MaxDuty':1023},{'Min':1,'Max':6,'MinDuty':0,'MaxDuty':1023}]
        if port == None:
            findmcu = mcuScan(baudrate)
            if len(findmcu) > 0:
                self.mcuserial = serial.Serial(findmcu.items()[0][0],baudrate, timeout=1)
                self.mcuserial.write('i' + chr(1) + chr(0))
                checkID = self.mcuserial.read(6)
                self.mcuType = int(checkID[5:])
                self.active = self.mcuserial.isOpen()
            else:
                sys.stderr.write('No pyMCU Module(s) Found!\n')
        else:
            try:
                self.mcuserial = serial.Serial(port,baudrate,timeout=1)
            except:
                sys.stderr.write('No pyMCU Module Found on port: ' + str(port) + '\n')
                return
            self.active = self.mcuserial.isOpen()
            if self.active == False:
                sys.stderr.write('No pyMCU Module Found on port: ' + str(port) + '\n')
            else:
                self.mcuserial.write('i' + chr(1) + chr(0))
                checkID = self.mcuserial.read(6)
                print checkID
                self.mcuType = int(checkID[5:])
                if 'pymcu' not in checkID:
                    sys.stderr.write('No pyMCU Module Found on port: ' + str(port) + '\n')
            
    def __str__(self):
        return "pymcu is on port %s at %d baudrate" %(self.mcuserial.portstr, self.mcuserial.baudrate)

    def __bitmask__(self, pinList):
        btL = [0,0,0,0,0,0,0,0]
        btH = [1,0,0,0,0,0,0,0]
        for x in range(0,9,1):
            for i in pinList:
                if i == x:
                    btL[8-x] = 1
        y = 1
        for x in range(9,14,1):
            for i in pinList:
                if i == x:
                    btH[8-y] = 1
            y += 1
        btL2 = ''
        for i in btL:
            btL2 += str(i)
        bL = int(btL2, 2)
        btH2 = ''
        for i in btH:
            btH2 += str(i)
        bH = int(btH2, 2)
        return bL, bH

    def mcuVersion(self):
        """return pymcu version on chip"""
        if self.active:
            self.mcuserial.write('v' + chr(0) + chr(0))
            return self.mcuserial.read(30)
        else:
            sys.stderr.write('pyMCU Is Currently Not Connected!\n')
    
    def mcuInfo(self):
        """Show Info About The Currently Connected pymcu"""
        if self.active:
            print '\nVersion Info         \t: ' + self.mcuVersion()
            print 'Available Digital Pins \t: ' + str(self.DPins[self.mcuType]['Min']) + ' - ' + str(self.DPins[self.mcuType]['Max'])
            print 'Available Analog Pins  \t: ' + str(self.APins[self.mcuType]['Min']) + ' - ' + str(self.APins[self.mcuType]['Max'])
            print 'Analog Value Range     \t: ' + str(self.APins[self.mcuType]['MinValue']) + ' - ' + str(self.APins[self.mcuType]['MaxValue'])
            print 'PWM Pins               \t: ' + str(self.PWMPins[self.mcuType]['Min']) + ' - ' + str(self.PWMPins[self.mcuType]['Max'])
            print 'PWM Duty Cycle Range   \t: ' + str(self.PWMPins[self.mcuType]['MinDuty']) + ' - ' + str(self.PWMPins[self.mcuType]['MaxDuty'])
            print 'COM Port:              \t: ' + str(self.mcuserial.portstr)
            print 'Baudrate:              \t: ' + str(self.mcuserial.baudrate) + '\n'
        else:
            sys.stderr.write('pyMCU Is Currently Not Connected!\n')

    def mcuSetBaudRate(self, baudrate):
        """Set the MCU Baud Rate (Change will take effect after next power cycle)
        0 = 2400
        1 = 4800
        2 = 9600
        3 = 19200
        4 = 38400
        5 = 57600
        6 = 115200
        Example Set Baud to 19200: mcuSetBaudRate(3)
        """
        if self.active:
            if baudrate >= 0 and baudrate <= 6:
                self.mcuserial.write('b' + chr(baudrate) + chr(0))
                eb = ""
                while eb != "eb":
                    eb = self.mcuserial.read(2)
            else:
                sys.stderr.write('Invalid Baud Rate Value, Valid Values are [0-6] See Help For More Details\n')
        else:
            sys.stderr.write('pyMCU Is Currently Not Connected!\n')
            
    def digitalState(self,pinNum, io):
        """Set State of Digital Pin as Input or Output (All Digital Pins Are Configured As Output By Default)
        Example Input: digitalState(1, 'input')
        Example Output: digitalState(1, 'output')
        or
        Example Input: digitalState(1, 1)
        Example Output: digitalState(1,0)"""
        if self.active:
            if pinNum < self.DPins[self.mcuType]['Min'] or pinNum > self.DPins[self.mcuType]['Max']:
                sys.stderr.write('Digital Pin Number is Out of Range: [' + str(self.DPins[self.mcuType]['Min']) + '-' + str(self.DPins[self.mcuType]['Max']) + ']\n')
                return
            if type(io) == str:
                if io.lower() == 'input':
                    self.mcuserial.write('=' + chr(pinNum) + chr(1))
                elif io.lower() == 'output':
                    self.mcuserial.write('=' + chr(pinNum) + chr(0))
                else:
                    sys.stderr.write('Need to Specify either "input" or "output"')
                    return
            elif type(io) == int:
                if io == 1:
                    self.mcuserial.write('=' + chr(pinNum) + chr(1))
                elif io == 0:
                    self.mcuserial.write('=' + chr(pinNum) + chr(0))
                else:
                    sys.stderr.write('Need to Specify either 1 for input or 0 for output')
                    return
        else:
            sys.stderr.write('pyMCU Is Currently Not Connected!\n')

    def digitalRead(self,pinNum):
        """Read Digital Pin State
        Example: digitalRead(1)
        Returns 0 or 1"""
        if self.active:
            if pinNum < self.DPins[self.mcuType]['Min'] or pinNum > self.DPins[self.mcuType]['Max']:
                sys.stderr.write('Digital Pin Number is Out of Range: [' + str(self.DPins[self.mcuType]['Min']) + '-' + str(self.DPins[self.mcuType]['Max']) + ']\n')
                return
            self.mcuserial.write('r' + chr(pinNum) + chr(0))
            bt = self.mcuserial.read(1)
            if bt == '0' or bt == '1':
                return int(bt)
            else:
                return 0
        else:
            sys.stderr.write('pyMCU Is Currently Not Connected!\n')
        
    def pwmOn(self, pwmPin):
        """Turn a PWM Pin On
        Example PWM On:  pwmOn(1)"""
        if self.active:
            if pwmPin < self.PWMPins[self.mcuType]['Min'] or pwmPin > self.PWMPins[self.mcuType]['Max']:
                sys.stderr.write('PWM Pin Number is Out of Range: [' + str(self.PWMPins[self.mcuType]['Min']) + ' - ' + str(self.PWMPins[self.mcuType]['Max']) + ']\n')
                return
            self.mcuserial.write('m' + chr(pwmPin) + chr(1))
        else:
            sys.stderr.write('pyMCU Is Currently Not Connected!\n')

    def pwmOff(self, pwmPin):
        """Turn a PWM Pin Off
        Example PWM Off:  pwmOff(1)"""
        if self.active:
            if pwmPin < self.PWMPins[self.mcuType]['Min'] or pwmPin > self.PWMPins[self.mcuType]['Max']:
                sys.stderr.write('PWM Pin Number is Out of Range: [' + str(self.PWMPins[self.mcuType]['Min']) + ' - ' + str(self.PWMPins[self.mcuType]['Max']) + ']\n')
                return
            self.mcuserial.write('m' + chr(pwmPin) + chr(0))
        else:
            sys.stderr.write('pyMCU Is Currently Not Connected!\n')

    def pwmDuty(self, pwmPin, duty = 500):
        """Set PWM Duty Cycle
        Example:  pwmDuty(1, 500)"""
        if self.active:
            if pwmPin < self.PWMPins[self.mcuType]['Min'] or pwmPin > self.PWMPins[self.mcuType]['Max']:
                sys.stderr.write('PWM Pin Number is Out of Range: [' + str(self.PWMPins[self.mcuType]['Min']) + ' - ' + str(self.PWMPins[self.mcuType]['Max']) + ']\n')
                return
            if duty < self.PWMPins[self.mcuType]['MinDuty'] or duty > self.PWMPins[self.mcuType]['MaxDuty']:
                sys.stderr.write('PWM Duty Cycle is Out of Range: [' + str(self.PWMPins[self.mcuType]['MinDuty']) + ' - ' + str(self.PWMPins[self.mcuType]['MaxDuty']) + ']\n')
                return
            self.mcuserial.write('w' + chr(pwmPin) + chr(0))
            bL = duty & 255
            bH = duty >> 8
            self.mcuserial.write('w' + chr(bL) + chr(bH))
        else:
            sys.stderr.write('pyMCU Is Currently Not Connected!\n')

    def analogRead(self,pinNum):
        """Read Analog Pin Value
        Example: analogRead(1)"""
        if self.active:
            if pinNum < self.APins[self.mcuType]['Min'] or pinNum > self.APins[self.mcuType]['Max']:
                sys.stderr.write('Analog Pin Number is Out of Range: [' + str(self.APins[self.mcuType]['Min']) + ' - ' + str(self.APins[self.mcuType]['Max'])+ ']\n')
                return
            self.mcuserial.write('a' + chr(pinNum) + chr(0))
            bt = self.mcuserial.read(4)
            bt = int('0x' + bt, 0)
            return int(bt)
        else:
            sys.stderr.write('pyMCU Is Currently Not Connected!\n')

    def soundOut(self, pinNum, note = 100, duration = 10):
        """Generates tone and/or white noise on the specified Pin.
        Note 0 is silence. Notes 1-127 are tones. Notes 128-255 are white noise.
        Tones and white noises are in ascending order (i.e. 1 and 128 are the lowest frequencies, 127 and 255 are the highest).
        Note 1 is about 78.74Hz and Note 127 is about 10,000Hz.
        Duration is 0-255 and determines how long the Note is played in about 12 millisecond increments.
        [soundOut will halt your program until the sound playing is complete]"""
        if self.active:
            if self.mcuType == 0:
                if pinNum < self.DPins[self.mcuType]['Min'] or pinNum > self.DPins[self.mcuType]['Max']:
                    sys.stderr.write('Digital Pin Number is Out of Range: [' + str(self.DPins[self.mcuType]['Min']) + '-' + str(self.DPins[self.mcuType]['Max']) + ']\n')
                    return
                if note < 0 or note > 255:
                    sys.stderr.write('Note value is out of range: [0-255]\n')
                    return
                if duration < 0 or duration > 255:
                    sys.stderr.write('Duration value is out of range: [0-255]\n')
                    return
                self.mcuserial.write('s' + chr(pinNum) + chr(note))
                self.mcuserial.write('s' + chr(duration) + chr(0))
                sd = ""
                while sd != "sd":
                    sd = self.mcuserial.read(2)
            else:
                sys.stderr.write('Your current pyMCU board does not support this feature.\n')
        else:
            sys.stderr.write('pyMCU Is Currently Not Connected!\n')


    def dtmfOut(self, pinNum, dtmfNum):
        """DTMF Tones Out on Digital Pin
        dtmfOut(pinNumber, DTMF Digit 0-9)
        Example: freqOut(4, 3)
        [dtmfOut will halt your program until the DTMF tone is complete]"""
        if self.active:
            if self.mcuType == 0:
                if pinNum < self.DPins[self.mcuType]['Min'] or pinNum > self.DPins[self.mcuType]['Max']:
                    sys.stderr.write('Digital Pin Number is Out of Range: [' + str(self.DPins[self.mcuType]['Min']) + '-' + str(self.DPins[self.mcuType]['Max']) + ']\n')
                    return
                if dtmfNum < 0 or dtmfNum > 9:
                    sys.stderr.write('DTMF Number is Out of Range: [0-9]\n')
                    return
                self.mcuserial.write('d' + chr(pinNum) + chr(dtmfNum))
                dd = ""
                while dd != "dd":
                    dd = self.mcuserial.read(2)
            else:
                sys.stderr.write('Your current pyMCU board does not support this feature.\n')
        else:
            sys.stderr.write('pyMCU Is Currently Not Connected!\n')

    def freqOut(self, pinNum, duration = 1000, freq1 = 0, freq2 = 0 ):
        """Frequency Out on Digital Pin
        freqOut(pinNumber, Duration in ms, Frequency 1, [Optional Frequency 2])
        Example: freqOut(4, 2000, 1000) - Play 1Khz tone on Digital Pin 4 for 2 Seconds
        [freqOut will halt your program for the frequency duration]"""
        if self.active:
            if self.mcuType == 0:
                if pinNum < self.DPins[self.mcuType]['Min'] or pinNum > self.DPins[self.mcuType]['Max']:
                    sys.stderr.write('Digital Pin Number is Out of Range: [' + str(self.DPins[self.mcuType]['Min']) + '-' + str(self.DPins[self.mcuType]['Max']) + ']\n')
                    return
                if duration < 1 or duration > 65535:
                    sys.stderr.write('Duration Value is Out of Range: [1-65535]\n')
                    return
                if freq1 < 0 or freq1 > 65535:
                    sys.stderr.write('Frequency Value 1 is Out of Range: [1-65535]\n')
                    return
                if freq2 < 0 or freq2 > 65535:
                    sys.stderr.write('Frequency Value 2 is Out of Range: [1-65535]\n')
                    return
                if freq2 != 0:
                    self.mcuserial.write('f' + chr(pinNum) + chr(2))
                else:
                    self.mcuserial.write('f' + chr(pinNum) + chr(1))
                bL = freq1 & 255
                bH = freq1 >> 8
                self.mcuserial.write('f' + chr(bL) + chr(bH))
                if freq2 != 0:
                    bL = freq2 & 255
                    bH = freq2 >> 8
                    self.mcuserial.write('f' + chr(bL) + chr(bH))
                bL = duration & 255
                bH = duration >> 8
                self.mcuserial.write('f' + chr(bL) + chr(bH))
                fd = ""
                while fd != "fd":
                    fd = self.mcuserial.read(2)
            else:
                sys.stderr.write('Your current pyMCU board does not support this feature.\n')
        else:
            sys.stderr.write('pyMCU Is Currently Not Connected!\n')

    def i2cRead(self, control, address, numBytes ):
        """ I2C Read from device
        Example: i2cRead(160,0,2) - Set Control Value to 160, Read Address 0, Read 2 Bytes
        returns a list item of read data"""
        if self.active:
            if self.mcuType == 0:
                self.mcuserial.write('k' + chr(4) + chr(numBytes))
                self.mcuserial.write(chr(11) + chr(control) + chr(address))
                it = self.mcuserial.read(numBytes)
                i2cdata = []
                for i in it:
                    i2cdata.append(ord(i))
                return i2cdata
            else:
                sys.stderr.write('Your current pyMCU board does not support this feature.\n')
        else:
            sys.stderr.write('pyMCU Is Currently Not Connected!\n')


    def i2cWrite(self, control, address, writeData):
        """ I2C Write to device
        Example: i2cWrite(160,0,100) - Set Control Value to 160, Write Address 0, Write 100"""
        if self.active:
            if self.mcuType == 0:
                byteArray = ''
                if type(writeData) == str:
                    byteArray = writeData

                if type(writeData) == int:
                    byteArray = chr(writeData)

                if type(writeData) == list or type(writeData) == tuple:
                    for i in writeData:
                        byteArray += chr(i)

                numBytes = len(byteArray)
                self.mcuserial.write('j' + chr(4) + chr(numBytes))
                self.mcuserial.write(chr(11) + chr(control) + chr(address) + byteArray)
                ic = ""
                while ic != "ic":
                    ic = self.mcuserial.read(2)
                    if ic == 'ix':
                        sys.stderr.write('i2c Ack Error\n')
                        ic = 'ic'
                        return
            else:
                sys.stderr.write('Your current pyMCU board does not support this feature.\n')
        else:
            sys.stderr.write('pyMCU Is Currently Not Connected!\n')

    def owWrite(self, pinNum, mode, writeData):
        """ 1-Wire Write to device
        owWrite(pinNumber, Mode, writeData)
        Mode is a 3 bit number:
        bit 0: 1 = Send reset pulse before data
        bit 1: 1 = Send reset after data
        bit 2: 0 = byte sized data, 1 = bit sized data
        Example: owWrite(1,1,100) - Write on pin 1 with mode set to only reset before pulse and byte sized data, write data 100"""
        if self.active:
            if self.mcuType == 0:
                byteArray = ''
                if type(writeData) == str:
                    byteArray = writeData

                if type(writeData) == int:
                    byteArray = chr(writeData)

                if type(writeData) == list or type(writeData) == tuple:
                    for i in writeData:
                        byteArray += chr(i)

                numBytes = len(byteArray)
                self.mcuserial.write('o' + chr(pinNum) + chr(numBytes))
                self.mcuserial.write(chr(mode) + byteArray)
                iw = ""
                while iw != "iw":
                    iw = self.mcuserial.read(2)

                return

            else:
                sys.stderr.write('Your current pyMCU board does not support this feature.\n')
        else:
            sys.stderr.write('pyMCU Is Currently Not Connected!\n')

    def owRead(self, pinNum, mode, numBytes ):
        """ 1-Wire Read from device
        owRead(pinNumber, Mode, numBytes)
        Mode is a 3 bit number:
        bit 0: 1 = Send reset pulse before data
        bit 1: 1 = Send reset after data
        bit 2: 0 = byte sized data, 1 = bit sized data
        Example: owRead(1,1,20) - Using Pin 1, send reset pulse before data, read 20 bytes
        returns a list item of read data"""
        if self.active:
            if self.mcuType == 0:
                self.mcuserial.write('t' + chr(pinNum) + chr(numBytes))
                self.mcuserial.write(chr(mode))
                iw = self.mcuserial.read(numBytes)
                oneWire = []
                for i in iw:
                    oneWire.append(ord(i))
                return oneWire
            else:
                sys.stderr.write('Your current pyMCU board does not support this feature.\n')
        else:
            sys.stderr.write('pyMCU Is Currently Not Connected!\n')

    def pulseIn(self, pinNum, state):
        """Measure Pulse Width on Digital Pin
        PulseIn(pinNumber, Pulse State)
        Pulse State of 1 will measure the width of a high pulse
        Pulse State of 0 will measure the width of a low pulse
        Example: pulseIn(4, 1)
        [PulseIn will halt your program until the pulse count is complete]"""
        if self.active:
            if self.mcuType == 0:
                if pinNum < self.DPins[self.mcuType]['Min'] or pinNum > self.DPins[self.mcuType]['Max']:
                    sys.stderr.write('Digital Pin Number is Out of Range: [' + str(self.DPins[self.mcuType]['Min']) + '-' + str(self.DPins[self.mcuType]['Max']) + ']\n')
                    return
                self.mcuserial.write('u' + chr(pinNum) + chr(state))
                pl = self.mcuserial.read(4)
                pl = int('0x' + pl, 0)
                return int(pl)
            else:
                sys.stderr.write('Your current pyMCU board does not support this feature.\n')
        else:
            sys.stderr.write('pyMCU Is Currently Not Connected!\n')

    def pulseOut(self, pinNum, pulse, count):
        """Pulse Out on Digital Pin
        PulseOut(pinNumber, Pulse Value, Pulse Repeat)
        The pulse is generated by toggling the pin twice,
        thus the initial state of the pin determines the polarity of the pulse
        Example: pulseOut(4, 500, 100)
        [PulseOut will halt your program until the pulse repeat cycle is complete]"""
        if self.active:
            if self.mcuType == 0:
                if pinNum < self.DPins[self.mcuType]['Min'] or pinNum > self.DPins[self.mcuType]['Max']:
                    sys.stderr.write('Digital Pin Number is Out of Range: [' + str(self.DPins[self.mcuType]['Min']) + '-' + str(self.DPins[self.mcuType]['Max']) + ']\n')
                    return
                if pulse < 1 or pulse > 65535:
                    sys.stderr.write('Pulse Value is Out of Range: [1-65535]\n')
                    return
                if count < 1 or count > 255:
                    sys.stderr.write('Pulse Repeat Value is Out of Range: [1-255]\n')
                    return
                bL = pulse & 255
                bH = pulse >> 8
                self.mcuserial.write('p' + chr(pinNum) + chr(count))
                #time.sleep(0.1)
                self.mcuserial.write('p' + chr(bL) + chr(bH))
                pd = ""
                while pd != "pd":
                    pd = self.mcuserial.read(2)
            else:
                sys.stderr.write('Your current pyMCU board does not support this feature.\n')
        else:
            sys.stderr.write('pyMCU Is Currently Not Connected!\n')
            
    def pinHigh(self,pinNum):
        """Set a Digital Pin High
        Example: pinHigh(1)
        Example: pinHigh([1,3,4,8,11])"""
        if self.active:
            if type(pinNum) == int:
                if pinNum < self.DPins[self.mcuType]['Min'] or pinNum > self.DPins[self.mcuType]['Max']:
                    sys.stderr.write('Digital Pin Number is Out of Range: [' + str(self.DPins[self.mcuType]['Min']) + '-' + str(self.DPins[self.mcuType]['Max']) + ']\n')
                    return
                self.mcuserial.write('+' + chr(pinNum) + chr(0))
            if type(pinNum) == list or type(pinNum) == tuple:
                for x in pinNum:
                    if x < self.DPins[self.mcuType]['Min'] or x > self.DPins[self.mcuType]['Max']:
                        sys.stderr.write('Digital Pin Number is Out of Range: [' + str(self.DPins[self.mcuType]['Min']) + '-' + str(self.DPins[self.mcuType]['Max']) + ']\n')
                        return
                bL,bH = self.__bitmask__(pinNum)
                self.mcuserial.write('+' + chr(bL) + chr(bH))
        else:
            sys.stderr.write('pyMCU Is Currently Not Connected!\n')

    def pinLow(self,pinNum):
        """Set a Digital Pin Low
        Example: pinLow(1)
        Example: pinLow([1,3,4,8,11])"""
        if self.active:
            if type(pinNum) == int:
                if pinNum < self.DPins[self.mcuType]['Min'] or pinNum > self.DPins[self.mcuType]['Max']:
                    sys.stderr.write('Digital Pin Number is Out of Range: [' + str(self.DPins[self.mcuType]['Min']) + '-' + str(self.DPins[self.mcuType]['Max']) + ']\n')
                    return
                self.mcuserial.write('-' + chr(pinNum) + chr(0))
            if type(pinNum) == list or type(pinNum) == tuple:
                for x in pinNum:
                    if x < self.DPins[self.mcuType]['Min'] or x > self.DPins[self.mcuType]['Max']:
                        sys.stderr.write('Digital Pin Number is Out of Range: [' + str(self.DPins[self.mcuType]['Min']) + '-' + str(self.DPins[self.mcuType]['Max']) + ']\n')
                        return
                bL,bH = self.__bitmask__(pinNum)
                self.mcuserial.write('-' + chr(bL) + chr(bH))
        else:
            sys.stderr.write('pyMCU Is Currently Not Connected!\n')

    def eepromWrite(self, address, value ):
        """Write Byte to EEPROM Storage Address
        Example: eepromWrite(0, 't')
        Example: eepromWrite(10,100)"""
        if self.active:
            if address < 1 or address > 255:
                sys.stderr.write('EEPROM Address is Out of Range: [0-255]\n')
                return
            if type(value) == int:
                if value < 0 or value > 255:
                    sys.stderr.write('EEPROM Value is Out of Range: [0-255]\n')
                    return
                self.mcuserial.write('e' + chr(address) + chr(value))
                ed = ""
                while ed != "ed":
                    ed = self.mcuserial.read(2)
            if type(value) == str:
                if ord(value) < 0 or ord(value) > 255:
                    sys.stderr.write('EEPROM Value is Out of Range: [0-255]\n')
                    return
                self.mcuserial.write('e' + chr(address) + chr(ord(value)))
                ed = ""
                while ed != "ed":
                    ed = self.mcuserial.read(2)
        else:
            sys.stderr.write('pyMCU Is Currently Not Connected!\n')

    def eepromRead(self, address ):
        """Read Byte From EEPROM Storage Address
        Byte Values are Stored as Raw Byte Data if you are Retrieving
        Ascii Character Data use chr() on the Returned Read Data
        Example: eepromRead(0)
        Example: chr(eepromRead(10))"""
        if self.active:
            if address < 1 or address > 255:
                sys.stderr.write('EEPROM Address is Out of Range: [0-255]\n')
                return
            self.mcuserial.write('x' + chr(address) + chr(0))
            return self.mcuserial.read(1)
        else:
            sys.stderr.write('pyMCU Is Currently Not Connected!\n')
            
    def serialRead(self, pinNum, mode, timeout, numBytes ):
        """Read Serial Data With Digital Pin
        mode sets baudrate and state:
        0 = 2400 Driven True
        1 = 4800 Driven True
        2 = 9600 Driven True
        3 = 19200 Driven True
        4 = 2400 Driven Inverted
        5 = 4800 Driven Inverted
        6 = 9600 Driven Inverted
        7 = 19200 Driven Inverted
        8 = 2400 Open True
        9 = 4800 Open True
        10 = 9600 Open True
        11 = 19200 Open True
        12 = 2400 Open Inverted
        13 = 4800 Open Inverted
        14 = 9600 Open Inverted
        15 = 19200 Open Inverted
        numBytes is Currently Limited to 64 Characters at a time
        Example Read 10 Bytes of Serial Data at 9600 Baud Driven True with a timeout of 1 second: serialRead(4,2,1000,10)
        """
        if self.active:
            if pinNum < self.DPins[self.mcuType]['Min'] or pinNum > self.DPins[self.mcuType]['Max']:
                sys.stderr.write('Digital Pin Number is Out of Range: [' + str(self.DPins[self.mcuType]['Min']) + '-' + str(self.DPins[self.mcuType]['Max']) + ']\n')
                return
            if numBytes > 64:
                sys.stderr.write('Sorry Cannot Read Data Length Greater Than 64 With This Version of pyMCU\n')
                return
            self.mcuserial.write('y' + chr(pinNum) + chr(numBytes))
            tmL = timeout & 255
            tmH = timeout >> 8
            self.mcuserial.write('y' + chr(mode) + chr(tmL) + chr(tmH))
            self.mcuserial.timeout = int(timeout / 1000)
            sr = self.mcuserial.read(numBytes)
            self.mcuserial.timeout = 1
            return sr
        else:
            sys.stderr.write('pyMCU Is Currently Not Connected!\n')

    def serialWrite(self, pinNum, mode, serialData ):
        """Write Serial Data With Digital Pin
        mode sets baudrate and state:
        0 = 2400 Driven True
        1 = 4800 Driven True
        2 = 9600 Driven True
        3 = 19200 Driven True
        4 = 2400 Driven Inverted
        5 = 4800 Driven Inverted
        6 = 9600 Driven Inverted
        7 = 19200 Driven Inverted
        8 = 2400 Open True
        9 = 4800 Open True
        10 = 9600 Open True
        11 = 19200 Open True
        12 = 2400 Open Inverted
        13 = 4800 Open Inverted
        14 = 9600 Open Inverted
        15 = 19200 Open Inverted
        String Data is Currently Limited to 64 Characters at a time
        Example Send a String, 9600 Driven Inverted on Pin 4: serialWrite(4, 6, 'Hello World')
        Example Send an Int, 9600 Driven True on Pin 5: serialWrite(5,2,100)
        You Can also Send Lists or Tuples Which Will Get Sent as Individual Serial Writes per Item
        Example: serialWrite(5,2,['Hello World\\r\\n','This is a test of Multiple Items', 'In a List\\r\\n'])
        """
        if self.active:
            if pinNum < self.DPins[self.mcuType]['Min'] or pinNum > self.DPins[self.mcuType]['Max']:
                sys.stderr.write('Digital Pin Number is Out of Range: [' + str(self.DPins[self.mcuType]['Min']) + '-' + str(self.DPins[self.mcuType]['Max']) + ']\n')
                return
            if type(serialData) == str:
                if len(serialData) > 64:
                    sys.stderr.write('Sorry Cannot Send String Data Length Greater Than 64 With This Version of pyMCU\n')
                    return
                self.mcuserial.write('q' + chr(pinNum) + chr(len(serialData)))
                self.mcuserial.write('q' + chr(mode) + serialData)
            if type(serialData) == int:
                if serialData >= 0 and serialData <= 255:
                    self.mcuserial.write('q' + chr(pinNum) + chr(1))
                    self.mcuserial.write('q' + chr(mode) + chr(serialData))
                else:
                    sys.stderr.write('Int Value Out of Range [0-255]\n')
                    return
            if type(serialData) == list or type(serialData) == tuple:
                for sd in serialData:
                    if type(sd) == str:
                        if len(sd) <= 64:
                            self.mcuserial.write('q' + chr(pinNum) + chr(len(sd)))
                            self.mcuserial.write('q' + chr(mode) + sd)
                            time.sleep(0.1)
                    if type(sd) == int:
                        if sd >= 0 and sd <= 255:
                            self.mcuserial.write('q' + chr(pinNum) + chr(1))
                            self.mcuserial.write('q' + chr(mode) + chr(sd))
                            time.sleep(0.1)
        else:
            sys.stderr.write('pyMCU Is Currently Not Connected!\n')


    def lcd(self,line=0,text=''):
        """Init or send text to the LCD
        Example Init LCD: lcd()
        Example send text to line 1: lcd(1,'Hello World')
        Example send text to line 2: lcd(2,'This is a test')
        Supports up to 4 line LCD"""
        if self.active:
            if line < 0 or line > 4:
                sys.stderr.write('Only 1-4 Line LCD\'s are Supported\n')
                return
            if len(text) > 32:
                sys.stderr.write('32 Characters Max For Text Line\n')
                return
            if line == 0:
                self.mcuserial.write('l' + chr(0) + chr(0))
            else:
                self.mcuserial.write('l' + chr(line) + chr(len(text)))
                self.mcuserial.write(text)
        else:
            sys.stderr.write('pyMCU Is Currently Not Connected!\n')
        
    def close(self):
        """Close MCU port access"""
        self.mcuserial.close()
        self.active = False
        return True

