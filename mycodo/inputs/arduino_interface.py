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
    'input_name_unique': 'arduino_interface',
    'input_manufacturer': 'arduino',
    'input_name': 'arduino_interface',
    'input_library': 'json',
    'measurements_name': 'CO2/VOC/Temperature/Humidity',
    'measurements_dict': measurements_dict,
    'url_manufacturer': 'https://github.com/andycb/AirQualityMonitor',
    'url_datasheet': 'https://andybradford.dev/2019/11/29/monitoring-my-indoor-air-quality/',
    'url_product_purchase': [
        'https://at.rs-online.com/web/p/temperatursensoren-und-feuchtigkeitssensoren/2036943/',
        'https://at.rs-online.com/web/p/luftgutesensoren/1024162/'
    ],

    'options_enabled': [
        'i2c_location',
        'measurements_select',
        'period',
        'pre_output'
    ],
    'options_disabled': ['interface'],

    'dependencies_module': [
        ('pip-pypi', 'serial', 'serial'),
    ],
    'interfaces': ['UART'],
    'uart_location': '/dev/ttyAMA0',
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

        self.sensor = None

        if not testing:
            self.initialize_input()

    def initialize_input(self):
        import serial 
        import json

        self.sensor = arduino_interface(
            address=int(str(self.input_dev.uart_location), 16),
            busnum=self.input_dev.i2c_bus)

        while not self.sensor.available():
            time.sleep(0.1)

        self.sensor.tempOffset = self.sensor.calculateTemperature() - 25.0

    def get_measurement(self):
        """ Gets the CO2, humidity, and temperature """
        if not self.sensor:
            self.logger.error("Input not set up")
            return

        self.return_dict = copy.deepcopy(measurements_dict)

        if self.sensor.available():
            temp = self.sensor.calculateTemperature()
            if not self.sensor.readData():
                self.value_set(0, self.sensor.geteCO2())
                self.value_set(1, self.sensor.getTVOC())
                self.value_set(2, temp)
            else:
                self.logger.error("Sensor error")
                return

            return self.return_dict
