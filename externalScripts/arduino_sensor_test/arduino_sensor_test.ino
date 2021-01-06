




int temperature = 20;
int co2Ppm = 200;
int tvocPpm = 200;
int humidity = 50;








void setup() 
{
  Serial.begin(9600);
}



void loop()
{     
  temperature += random(5) - 2;
  co2Ppm += random(21) - 10;
  tvocPpm += random(21) - 10;
  humidity += random(5) - 2;

  // Build out the JSON object the hard way

    //   obj = {
    //     status: true,
    //     errorText: '',
    //     iaQStatus: 0,
    //     co2: 100, 
    //     tvoc: 200,
    //     temp: 20,
    //     humidity: 40
    // };

  Serial.print("{");
  Serial.print("\"status\":");
  Serial.print(0);
  Serial.print(",");  

  Serial.print("\"iaQStatus\":");
  Serial.print(0);
  Serial.print(",");  
  
  Serial.print("\"co2\":");
  Serial.print(co2Ppm);
  Serial.print(",");  

  Serial.print("\"tvoc\":");
  Serial.print(tvocPpm);
  Serial.print(",");  
  
  Serial.print("\"temp\":");
  Serial.print(temperature);
  Serial.print(",");  

  Serial.print("\"humidity\":");
  Serial.print(humidity);  
  
  Serial.println("}");

  delay(1000);
}
