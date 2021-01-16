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
        self.logger.debug("finished init")

    def initialize_input(self):
        import serial 

        uart_port = INPUT_INFORMATION['uart_location']
        rate = INPUT_INFORMATION['uart_baud_rate']
        self.serialPort = serial.Serial(port=uart_port, baudrate=rate, timeout=1)
        
        self.logger.debug("finished init input")

    def readSerialLine(self, ser):
        ser.flush()
    
        for i in range(300): # runs for 300 * 10 ms
            ser.flushInput()
            ser.flushOutput()
            ser.write(b'\n\r')
            line = ser.readline().decode('utf-8').rstrip()
            return line
            time.sleep(i/100.0)
        return None


    def get_measurement(self):
        import json
        """ Gets the CO2, humidity, and temperature """
        
        self.logger.debug("In get measurement")
        
        if not self.serialPort:
            self.logger.error("Input not set up")
            return
        
        #Necessary according to mycodo
        self.return_dict = copy.deepcopy(measurements_dict)
        
        #Getting data from arduino
        line = self.readSerialLine(self.serialPort)
        
        if(line): #See if recieved line is valid
        
            line = line.strip()
            try:
                try:
                    self.jsonObject = json.loads(line)
    
                except Exception as msg:
                    self.logger.exception("Problem reading json data: {}"\
                                          .format(msg))               
            
                hih_error = False
                iaq_error = False
                #Handling of error codes coming from the arduino

        

                
                #Possible problem with the humidity sensor
                if self.jsonObject["hihstatus"] != 0:
                    self.logger.error("Problem with HIH (temperat"\
                                                +"ure + humidity) sensor")
                    hih_error = True

                if self.jsonObject["iaQStatus"] != 0:
                    if self.jsonObject["iaQStatus"]  == 16:
                        self.logger.info("CO2 sensor heating up")

                    else:
                        self.logger.error("Problem with CO2 sensor")
                    iaq_error = True
                if self.jsonObject["errorstatus"] == 4: 
                    self.logger.error("HIH (temperature + humidity) sensor "\
                                       +"not ready for measurement")
                    hih_error = True

                        
                if  hih_error:
                    if self.is_enabled(2):  
                        self.value_set(2, 0) #Set temp measurement to 0
                    if self.is_enabled(3):  
                        self.value_set(3, 0) #Set humidity measurement to 0
                else:
                    if self.is_enabled(2):  # Only store the measurement if it's enabled
                        self.value_set(2, self.jsonObject["temp"])
                    if self.is_enabled(3):  # Only store the measurement if it's enabled
                        self.value_set(3, self.jsonObject["humidity"])                    
                if iaq_error:
                    if self.is_enabled(0):  
                        self.value_set(0, 0) #Set CO2 measurement to 0
                    if self.is_enabled(1):  
                        self.value_set(1, 0) #Set voc measurement to 0
                else:
                    if self.is_enabled(0):  # Only store the measurement if it's enabled
                        self.value_set(0, self.jsonObject["co2"])        
                    if self.is_enabled(1):  # Only store the measurement if it's enabled
                        self.value_set(1, self.jsonObject["tvoc"])    


                

                return self.return_dict
            except Exception as msg:
                self.logger.exception("Problem aquiring input from Arduino: {}"\
                                          .format(msg)) 
        else: #Send error if nothing was recieved
            self.logger.error("Unable to connect to Arduino")
            return
        
        
        
        
        
        

   
