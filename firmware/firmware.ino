#include "HX711.h"
#include "Streaming.h"

const uint8_t Dat_Pin = A1;
const uint8_t SCK_Pin = A0;
const uint8_t Gain = 128;
//const uint8_t Gain = 32;
const uint32_t Baudrate = 115200;

HX711 scale;

void setup() 
{

  Serial.begin(Baudrate);
  scale.begin(Dat_Pin, SCK_Pin, Gain);
  scale.power_up();

  scale.set_scale(20000.f);       
  scale.tare();				 
}

void loop() 
{
    static uint32_t count = 0;
    static uint32_t t_start_ms = millis();
    uint32_t t_elapsed_ms = millis() - t_start_ms;
    double t_elapsed_s = 1.0e-3*t_elapsed_ms;


    double value = scale.get_units(1);
    Serial << t_elapsed_s << " " << value << endl;
    //long raw = scale.read();
    //Serial << t_elapsed_s << " " << raw << endl;
    delay(1);
    count++;
}
