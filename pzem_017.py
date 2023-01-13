#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 15 22:46:59 2022

@author: sudarsun
"""

import minimalmodbus
import time

class PZEM017:
    """ wrapper to access PZEM-017 device as a MODBUS slave """
    def __init__(self, device, identifier, address=1, baudrate=9600, timeout=5, stopbits=2):
        self._device = minimalmodbus.Instrument(device, address, mode=minimalmodbus.MODE_RTU, close_port_after_each_call=True)
        self._device_path = device
        self._device.serial.baudrate = baudrate
        self._device.serial.timeout = timeout
        self._device.serial.stopbits = stopbits
        self._shunts = {1:"100A", 2:"50A", 3:"200A", 4:"300A"}
        self._id = identifier
        self._retries = 0

    def __retry_mechanism(self, function, *args):
        """ Retry mechanism for executing the MODBUS reads """
        retry = 0
        while retry <= self._retries:
            try:
                # this delay is needed for proper functioning.
                time.sleep(0.05)
                arglen = len(args)
                if arglen == 0:
                    return function()
                elif arglen == 1:
                    return function(args[0])
                elif arglen == 2:
                    return function(args[0], args[1])
                elif arglen == 3:
                    return function(args[0], args[1], args[2])
                elif arglen == 4:
                    return function(args[0], args[1], args[2], args[3])
                else:
                    return function()
            except (minimalmodbus.NoResponseError, IOError) as e:
                retry += 1
                # if we have reached the upper cutoff, rethrow.
                if retry == self._retries:
                    raise e
                time.sleep(1)
                continue
        raise ValueError(f"elapsed maximum retries ({self._retries}) calling the function", function)

    @property
    def name(self):
        """ get the name of the device """
        return self._id

    @property
    def retries(self):
        return self._retries

    @retries.setter
    def retries(self, count):
        self._retries = count

    @property
    def voltage(self):
        """ read the voltage at the precision of 0.1V"""
        return self.__retry_mechanism(self._device.read_register, 0, 2, 4)

    @property
    def current(self, retries=0):
        """ read the current value at a precision of 0.1A"""
        return self.__retry_mechanism(self._device.read_register, 1, 2, 4)

    @property
    def power(self, retries=0):
        """ read the power value (32bit) at a precision of 0.1W"""
        pl = self.__retry_mechanism(self._device.read_register, 2, 1, 4)
        ph = self.__retry_mechanism(self._device.read_register, 3, 1, 4)
        p = ph * 65536 + pl
        return p

    @property
    def energy(self, retries=0):
        """ read energy value (32bit) as an integer in Wh"""
        el = self.__retry_mechanism(self._device.read_register, 4, 0, 4)
        eh = self.__retry_mechanism(self._device.read_register, 5, 0, 4)
        e = eh * 65536 + el
        return e

    @property
    def address(self):
        """ get the device address """
        return self._device.read_register(2)

    @address.setter
    def address(self, new_address):
        """ change the device's MODBUS address """
        self._device.write_register(2, new_address, functioncode=6)
        # now reinitialize the object to continue talking to the device
        # in the new address.
        self.__init__(self._device_path, self._id,
                      address=self._device.address,
                      baudrate=self._device.serial.baudrate,
                      timeout=self._device.serial.timeout,
                      stopbits=self._device.serial.stopbits)

    @property
    def low_voltage_alarm(self):
        """ get the low voltage alarm threshold voltage """
        self._device.read_register(1)

    @low_voltage_alarm.setter
    def low_voltage_alarm(self, lvalarm):
        """ set the low voltage alarm threshold voltage """
        self._device.write_register(1, lvalarm, functioncode=6)

    @property
    def high_voltage_alarm(self):
        """ get the high voltage alarm threshold voltage """
        self._device.read_register(0)

    @high_voltage_alarm.setter
    def high_voltage_alarm(self, hvalarm):
        """ set the high voltage alarm threshold voltage """
        self._device.write_register(0, hvalarm, functioncode=6)

    @property
    def shunt_type(self):
        """ get the shunt current range configuration """
        s = self._device.read_register(3)
        return self._shunts[s], s

    @shunt_type.setter
    def shunt_type(self, shunt):
        """ set the shunt current range configuration """
        self._device.write_register(3, shunt, functioncode=6)

    def shunt_name(self, shunt):
        """ convert code to shunt name string """
        return self._shunts[shunt]
