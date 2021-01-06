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
        self.serialPort = serial.Serial(port=uart_port, baudrate=rate, timeout=1)

    def readSerialLine(self, ser):
        ser.flush()
    
        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').rstrip()
                return line



    def get_measurement(self):
        import sys
        import json
        """ Gets the CO2, humidity, and temperature """
        if not self.serialPort:
            self.logger.error("Input not set up")
            return

        self.return_dict = copy.deepcopy(measurements_dict)
        
        line = self.readSerialLine(self.serialPort)
        
        line = line.strip()


        self.jsonObject = json.loads(line)


        self.logger.info(
            "This INFO message will always be displayed. "
            "Acquiring measurements...")
        
        if self.is_enabled(0):  # Only store the measurement if it's enabled
            self.value_set(0, self.jsonObject["co2"])
            
        if self.is_enabled(1):  # Only store the measurement if it's enabled
            self.value_set(1, self.jsonObject["tvoc"])

        if self.is_enabled(2):  # Only store the measurement if it's enabled
            self.value_set(2, self.jsonObject["temp"])

        if self.is_enabled(3):  # Only store the measurement if it's enabled
            self.value_set(3, self.jsonObject["humidity"])



        return self.return_dict
        
        
        
        
        
        

   
