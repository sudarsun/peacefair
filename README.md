# peacefair
MODBUS wrapper class to access PZEM devices.  Currently supporting PZEM-017 with external shunt.

## Reading the measurements from the device

```python
from peacefair import PZEM017

# device is the path to the USB device
# address is the address configuration of the device (default is 1)
dev = PZEM017(device='/dev/ttyUSB0', identifier="Solar", address=1)

# read the voltage
v = dev.voltage

# read the current
c = dev.current

# read the power
p = dev.power

# read the energy 
e = dev.energy
```

## Reading and updating the configuration settings

```python
# read the address
a = dev.address

# set a new address
# beware: current 'dev' object will no longer be able to fetch results from the device
#         new dev object should be created.
dev.address = 10

# read the high voltage alarm value
v_high = dev.high_voltage_alarm

# set the high voltage alarm value
v_high = 200
dev.high_voltage_alarm = v_high

# read the high voltage alarm value
v_low = dev.low_voltage_alarm

# set the low voltage alarm value
dev.low_voltage_alarm = 50

# get the shunt type
shunt = dev.shunt_type

# set the shunt type
dev.shunt_type = 2

# get the shunt name
# 1:"100A", 2:"50A", 3:"200A", 4:"300A"
name = dev.shunt_name(2)

```
