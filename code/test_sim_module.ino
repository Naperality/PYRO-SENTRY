#include <SoftwareSerial.h>

SoftwareSerial sim800(7, 8);

void setup()
{
    Serial.begin(9600);
    sim800.begin(9600);

    delay(3000);

    sim800.println("AT");
}

void loop()
{
}