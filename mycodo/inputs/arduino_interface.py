# coding=utf-8
import time

import copy

from mycodo.inputs.base_input import AbstractInput

# Measurements
measurements_dict = {
    0: {
        'measurement': 'co2',
        'unit': 'ppm'
    },
    1: {
        'measurement': 'voc',
        'unit': 'ppb'
    },
    2: {
        'measurement': 'temperature',
        'unit': 'C'
    },
    3: {
        'measurement': 'humidity',
        'unit': 'percent'
    }
}

# Input information
INPUT_INFORMATION = {
    'input_name_unique': 'Arduino_interface',
    'input_manufacturer': 'Arduino',
    'input_name': 'Arduino_interface',
    'input_library': 'json',
    'measurements_name': 'CO2/VOC/Temperature/Humidity',
    'measurements_dict': measurements_dict,
    'measurements_use_same_timestamp': True,
    
    'url_manufacturer': 'https://github.com/andycb/AirQualityMonitor',
    'url_datasheet': 'https://andybradford.dev/2019/11/29/monitoring-my-indoor-air-quality/',
    'url_product_purchase': [
        'https://at.rs-online.com/web/p/temperatursensoren-und-feuchtigkeitssensoren/2036943/',
        'https://at.rs-online.com/web/p/luftgutesensoren/1024162/'
    ],

    'options_enabled': [
        'uart_location',
        'measurements_select',
        'period',
        'pre_output'
    ],
    'options_disabled': ['interface'],

    'dependencies_module': [
        ('pip-pypi', 'serial', 'pyserial'),
    ],
    'interfaces': ['UART'],
    'uart_location': '/dev/ttyUSB0',
    'uart_baud_rate': 9600,
    'uart_address_editable': True
}


class InputModule(AbstractInput):
    """
    A sensor support class that interfaces with CO2, temperature and humidity 
    sensors via an arduino using UART
    """
    def __init__(self, input_dev, testing=False):
        super(InputModule, self).__init__(input_dev, testing=testing, name=__name__)

        self.last_received = None
        self.serialPort = None
        self.jsonObject = None

        if not testing:
            self.initialize_input()

    def initialize_input(self):
        import serial 

        uart_port = INPUT_INFORMATION['uart_location']
        rate = INPUT_INFORMATION['uart_baud_rate']
        self.serialPort = serial.Serial(port=uart_port, baudrate=rate)

    def readSerialLine(self, ser):
        buffer_string = ''
        while True:
            buffer_string = buffer_string + ser.read(ser.inWaiting())
            if '\n' in buffer_string:
                lines = buffer_string.split('\n') # Guaranteed to have at least 2 entries
                self.last_received = lines[-2]
                buffer_string = lines[-1]
    
                return self.last_received


    def get_measurement(self):
        import sys
        import json
        """ Gets the CO2, humidity, and temperature """
        if not self.serialPort:
            self.logger.error("Input not set up")
            return

        self.return_dict = copy.deepcopy(measurements_dict)
        
        try:
            self.serialPort.flushOutput()
            self.serialPort.flushInput()
            self.serialPort.write("\n\r")
            self.serialPort.write("\n\r")
            
            self.serialPort.flushOutput()
            line = self.readSerialLine(self.serialPort)
            
            line = line.strip()
            
            try:
                try:
                    self.jsonObject = json.loads(line)
                    
                    if self.jsonObject["iaQStatus"] == 0:
                        
                        self.return_dict("Temp", str(self.jsonObject["temp"]) + "c")
                        self.logger.info("Option one value is {}".format(self.option_one))
            
                        self.logger.info(
                            "This INFO message will always be displayed. "
                            "Acquiring measurements...")
                        
                        if self.is_enabled(0):  # Only store the measurement if it's enabled
                            self.value_set(0, self.jsonObject["co2"])
                            
                        if self.is_enabled(2):  # Only store the measurement if it's enabled
                            self.value_set(2, self.jsonObject["tvoc"])
            
                        if self.is_enabled(2):  # Only store the measurement if it's enabled
                            self.value_set(2, self.jsonObject["temp"])
            
                        if self.is_enabled(3):  # Only store the measurement if it's enabled
                            self.value_set(3, self.jsonObject["humidity"])

                        
                    else:
                        # The IAQ-Core is not ready yet, any data it sends is invalid
                       
                        if self.jsonObject["iaQStatus"] == 160:
                            # The IAQ-Core needs to warm up when it first starts. This is normal
                            self.logger.info("Please wait", "Warmup")
                        else:
                            # Some other error happened. 
                            self.logger.error("Please wait"
                                              "Err" + str(self.jsonObject["iaQStatus"]))
    
                except ValueError as msg:
                    # The JSON object from the sensor modual was not valid, log the error and continue
                    self.logger.error("Exception: {}".format(msg))
    
#                except RequestError as msg:
#                    # Failed to connect to Adafruit IO, drop the reading and back off for two mins before retring.
#                    self.logger.error("Exception: {}".format(msg))
    
                    time.sleep(2 * 60)
            except:
                # Some other exception. Log the error continue.
                e = sys.exc_info()
                self.logger.error("Unhandled exception: " + str(e) + "\n")


        except:
            # Failed to communicate with the sensor modual. Log the error and continue.
            e = sys.exc_info()
            self.logger.error("Unhandled exception: " + str(e) + "\n")


        return self.return_dict
        
        
        
        
        
        

   
