#include "Wire.h"
#include "iAQcore.h"
#include <HIH61xx.h>
#include <AsyncDelay.h>

//Error codes

#define ERROR_NO_ERROR 0
#define ERROR_HIH_STARTUP 1
#define ERROR_HIH_HANDLER 2
#define ERROR_IAQ_NOT_STARTED 3


int error_state = ERROR_NO_ERROR;



//I2C bus pins on ESP8266
int sda = 4;
int scl = 5;

// The "hih" object must be created with a reference to the "Wire" object which represents the I2C bus it is using.
// Note that the class for the Wire object is called "TwoWire", and must be included in the templated class name.
HIH61xx<TwoWire> hih(Wire);

AsyncDelay samplingInterval;



//check if both sensors have been read
bool hih_read;



void powerUpErrorHandler(HIH61xx<TwoWire>& hih)
{
  error_state = ERROR_HIH_STARTUP;
}


void readErrorHandler(HIH61xx<TwoWire>& hih)
{
  error_state = ERROR_HIH_HANDLER;
}

void(* resetFunc) (void) = 0;


iAQcore iaqcore;

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
}


void loop()
{     

  if (samplingInterval.isExpired() && !hih.isSampling()) {
    hih.start();
    hih_read = false;
    samplingInterval.repeat();
  }

  hih.process();

  

  if (hih.isFinished() && !hih_read) {

      if(error_state){
        resetFunc();
      }

      
      hih_read = true;
      // Print saved values

      // Read hih
      int16_t temp;
      uint16_t rel_hum;
      uint16_t status_hih;
      
      rel_hum = hih.getRelHumidity();
      temp = hih.getAmbientTemp();
      status_hih = hih.getStatus();

      
      // Read iaq-core
      uint16_t eco2;
      uint16_t iaq_stat;
      uint32_t resist;
      uint16_t etvoc;
      
      iaqcore.read(&eco2,&iaq_stat,&resist,&etvoc);


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
}
