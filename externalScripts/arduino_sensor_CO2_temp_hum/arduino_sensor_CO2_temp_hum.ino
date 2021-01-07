#include "Wire.h"
#include "iAQcore.h"
#include <HIH61xx.h>
#include <AsyncDelay.h>

//Error codes

#define ERROR_NO_ERROR 0
#define ERROR_HIH_STARTUP 1
#define ERROR_HIH_HANDLER 2
#define ERROR_IAQ_NOT_STARTED 3
#define ERROR_NOT_READY 4 //hih not ready, wait


int error_state = ERROR_NO_ERROR;

uint16_t loop_counter;

//I2C bus pins on ESP8266
int sda = 4;
int scl = 5;

// The "hih" object must be created with a reference to the "Wire" object which represents the I2C bus it is using.
// Note that the class for the Wire object is called "TwoWire", and must be included in the templated class name.
HIH61xx<TwoWire> hih(Wire);

AsyncDelay samplingInterval;



//check if both sensors have been read
bool hih_read;

//Read request handles data aquisition request from raspi
bool read_request = false;



void powerUpErrorHandler(HIH61xx<TwoWire>& hih)
{
  error_state = ERROR_HIH_STARTUP;
}


void readErrorHandler(HIH61xx<TwoWire>& hih)
{
  error_state = ERROR_HIH_HANDLER;
}

// Calling this function resets microcontroller
void(* resetFunc) (void) = 0;



iAQcore iaqcore;

// Checks for read request from UART bus
bool check_read_request(){
  // Wait to recive some data before sending a reading
  if (Serial.available() > 0) 
  {
    while (Serial.available() > 0)
    {
      // Look for a line feed to be sent to us (ASCII 10)
      int incomingByte = Serial.read();
      if (incomingByte == 10) // '\n' in ASCII
      {
        return true;
      }
    }
  }
  else
  {
    return false;
  }
}

void setup() 
{
  Serial.begin(9600);
  
  Wire.begin(sda, scl);
  Wire.setClockStretchLimit(1000); // Default is 230us, see line78 of https://github.com/esp8266/Arduino/blob/master/cores/esp8266/core_esp8266_si2c.c

  // Set the handlers *before* calling initialise() in case something goes wrong
  hih.setPowerUpErrorHandler(powerUpErrorHandler);
  hih.setReadErrorHandler(readErrorHandler);
  hih.initialise();
  samplingInterval.start(3000, AsyncDelay::MILLIS);

  hih_read = false;


  // Enable iAQ-Core
  if(!iaqcore.begin()){
    // check if iaq-core did a proper startup
    error_state = ERROR_IAQ_NOT_STARTED;
  }
  loop_counter = 0;
}

void write_out_data(int16_t temp, uint16_t rel_hum,
      uint16_t status_hih, uint16_t eco2,
      uint16_t iaq_stat, uint32_t resist,
      uint16_t etvoc) {

      // Build out the JSON object the hard way

      //   obj = {
      //     status: true,
      //     errorText: '',
      //     iaQStatus: 0,
      //     co2: 100, 
      //     tvoc: 200,
      //     temp: 20,
      //     humidity: 40,
      //     pressure: 1000
      // };

      Serial.print("{");
      Serial.print("\"hihstatus\":");
      Serial.print(status_hih);
      Serial.print(",");  
    
      Serial.print("\"iaQStatus\":");
      Serial.print(iaq_stat);
      Serial.print(",");  

      Serial.print("\"errorstatus\":");
      Serial.print(error_state);
      Serial.print(","); 
      
      Serial.print("\"co2\":");
      Serial.print(eco2);
      Serial.print(",");  
    
      Serial.print("\"tvoc\":");
      Serial.print(etvoc);
      Serial.print(",");  
      
      Serial.print("\"temp\":");
      Serial.print(temp/100.0);
      Serial.print(",");  
    
      Serial.print("\"humidity\":");
      Serial.print(rel_hum/100.0);      
      Serial.println("}");

        
      }


void loop()
{     
  read_request = check_read_request();

   if(!samplingInterval.isExpired() && read_request) {
      error_state = ERROR_NOT_READY;
   }
   else if (samplingInterval.isExpired() && !hih.isSampling() &&
      read_request) {
    hih.start();
    hih_read = false;

    samplingInterval.repeat();
    error_state = ERROR_NO_ERROR;
  }
  

  hih.process();

  if (read_request) {

      
      hih_read = true;
      // Print saved values

      // Read hih
      int16_t temp;
      uint16_t rel_hum;
      uint16_t status_hih;

      if(! error_state){
        rel_hum = hih.getRelHumidity();
        temp = hih.getAmbientTemp();
        status_hih = hih.getStatus();
      }
      else {
        rel_hum = 0;
        temp = 0;
        status_hih = error_state;
      }


      
      // Read iaq-core
      uint16_t eco2;
      uint16_t iaq_stat;
      uint32_t resist;
      uint16_t etvoc;
      
      iaqcore.read(&eco2,&iaq_stat,&resist,&etvoc);

      write_out_data(temp, rel_hum, status_hih, eco2,
            iaq_stat, resist, etvoc);


      error_state = ERROR_NO_ERROR;
      read_request = false;
  }
  
  if(hih.isFinished() && !hih_read) {
    hih_read = true;
    error_state = ERROR_NO_ERROR;    
  }

  //THis function is needed as the I2C does not always initilize the iaq sensor correctly. If the sensor is missing some functionality is still guaranteed
  if(error_state == ERROR_IAQ_NOT_STARTED){
    loop_counter++;
    delay(10);
    if(loop_counter >= 30000){
      resetFunc(); //Reset about every 5 minutes
    }
  }
}
