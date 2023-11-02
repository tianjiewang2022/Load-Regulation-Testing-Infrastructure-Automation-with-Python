# TODO: check load regulation 
# apply varying voltage
# measure the actual output voltage using DM
# calculate the lr and check meet toleration?
# record in a file

# -----------------------//Method1 (USB)-----------------------
# Procedure (V and V0) Settings: Rated output V; Current: Max. limit
# 1. Turn on the power supply and set it to its rated output voltage. Ensure that the current adjust knob, if present, is set to its maximum value.
# 2. Write down the measured voltage of the power supply. Call this value V0.
# 3. Press I-set on the DC load to set to power supply's rated value.  Turn on the input of the load by pressing On/Off.
# 4. Write down the measured voltage of the power supply. Call this value V.
# Calculate the load regulation (in percent) of the power supply by 100 * (V0−V / V0)
# 5. Turn off the DC load's input by pressing the On-Off button.
# 6. Turn off the power supply.

import pyvisa 
import time
import os

rm = pyvisa.ResourceManager()

def check_load_regulation(filepath, time, supply_address, dm_address, toleration, startV, endV, intervalV, maxCurrent):
    # open the resource for the ps and dmm
    supply = rm.open_resource(supply_address)
    dmm = rm.open_resource(dm_address)

    # Setup DM in DC Voltage mode
    dmm.write(':FUNC:VOLT:DC')

    # Setup the PS: startV, maxCurrent
    supply.write(':OUTP CH1, OFF')
    supply.write(':OUTP CH1, ' + str(startV) + ', ' str(maxCurrent))

    # Run the test
    supply.write(':OUTP CH1, ON')

    # Main Script + error handling
    try:
        v = startV
        while v < endV:
            # Set the load on the PS
            supply.write(':APPL CH1, ' + str(v) + ', ' str(maxCurrent))
            time.sleep(time)

            # Measure the actual output voltage using DM
            vMeasure = float(dmm.query(':MEAS:VOLT:DC?'))

            # calculate the load regulation error
            load_regulation_error = abs(v - vMeasure) / v

            # record and comp
            with open(filepath, 'a') as file:
                if os.stat(filepath).st_size == 0:
                    file.write("Setpoint[V], Measure[V], Load Regulation Error[%]\n")
                file.write("{:.2f}, {:.2f}, {:.2f}\n".format(v, vMeasure, load_regulation_error))

            # Check and comp
            if load_regulation_error <= toleration:
                print(f"Load Regulation meets at {v}V")
            else:
                print(f"Load Regulation does not meet at {v}V")
            
            v += intervalV
    except KeyboardInterrupt:
        print("Script terminate by user")
    finally:
        # Close and clear the output
        supply.write(':OUTP CH1, OFF')
        supply.write(':OUTP CH1, 0, 0')
        # Close the SP and DM
        supply.close()
        dmm.close()
        rm.close()

# improve the code clearance and make it reuseable:
# def helper functions for setLoad(v, a) and measureV()
# temp = {} records.append(temp, ignore_index = True)
# def helper function for judge string ->? float()


# -----------------------//Method2 (Serial)-----------------------
# TODO: Write a script that steps through loads on a power supply and 
# determines if a load regulation requirement is met - Serial

import time
import serial  # For serial communication with the power supply
import visa  # For communication with the digital multimeter (DMM)

# Define the parameters
start_load = 0  # Start load in mA
end_load = 1000  # End load in mA
load_step = 100  # Load step in mA
load_regulation_threshold = 0.02  # Acceptable voltage regulation threshold in volts
# Define the expected voltage (adjust as per your needs)
expected_voltage = 5.0  # The voltage you expect to get under the specified load


# Initialize communication with the power supply
power_supply = serial.Serial('COM3', baudrate=9600)  # Replace 'COM3' with your power supply's serial port

# Initialize communication with the digital multimeter (DMM)
rm = visa.ResourceManager()
dmm = rm.open_resource('TCPIP0::192.168.1.100::inst0::INSTR')  # Replace with the DMM's address

# Function to set load on the power supply
def set_load(current):
    command = f"LOAD {current}\r\n"
    power_supply.write(command.encode())
    time.sleep(1)  # Allow time for the load to stabilize

# Function to measure voltage with the DMM
def measure_voltage():
    voltage = float(dmm.query("MEASURE:VOLTAGE:DC?"))
    return voltage

# Main script
try:
    for current in range(start_load, end_load + load_step, load_step):
        set_load(current)
        measured_voltage = measure_voltage()

        if abs(measured_voltage - expected_voltage) <= load_regulation_threshold:
            print(f"Load: {current} mA - Voltage within regulation threshold ({load_regulation_threshold} V)")
        else:
            print(f"Load: {current} mA - Voltage out of regulation threshold")

except KeyboardInterrupt:
    print("Script terminated by user")

finally:
    # Clean up and close connections
    power_supply.close()
    dmm.close()



# -----------------------//Method3-----------------------
import numpy as np 						# 1
import pandas as pd 						# 2
import visa, time						# 3
chroma = visa.instrument('GPIB::2')				# 4
daq = visa.instrument('GPIB::9')				# 5
results = pd.DataFrame()					# 6
loads = np.arange(0,20+2,2)					# 7
for load in loads:						# 8
# Measure the current and the voltage
# Save the results					# 8
	chroma.write('CURR:STAT:L1 %.2f' % load)		# 9
	chroma.write('LOAD ON')					# 10
	time.sleep(1)						# 11

	temp = {}						# 12
	daq.write('MEAS:VOLT:DC? AUTO,DEF,(@101)')		# 13	
    temp['Vout'] = float(daq.read())			# 14
	daq.write('MEAS:VOLT:DC? AUTO,DEF,(@102)')		# 15
	temp['Iout'] = float(daq.read())/0.004			# 16

    temp['Vout_id'] = 1.0 - 2.5e-3*temp['Iout'] 		# A
    temp['Vout_err'] = temp['Vout_id'] - temp['Vout'] 	# B	
    temp['Pass'] = 'Yes' 					# C
    if (abs(temp['Vout_err']) > temp['Vout_id']*0.001):	# D
        temp['Pass'] = 'No'				# E

	results = results.append(temp, ignore_index=True)	# 17
	print "%.2fAt%.3fV" % (temp['Iout'],temp['Vout'])	# 18
    chroma.write('LOAD OFF')					# 19
    results.to_csv('Results.csv')	





