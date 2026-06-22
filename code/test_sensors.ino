#include <DHT.h>

#define DHTPIN 4 // use A1 if arduino for analog
#define DHTTYPE DHT11

#define MQ2_PIN 34 // use A0 for arduino

DHT dht(DHTPIN, DHTTYPE);

void setup()
{
    Serial.begin(115200);

    dht.begin();

    Serial.println("PyroSentry Sensor Test");
}

void loop()
{
    float temperature = dht.readTemperature();
    float humidity = dht.readHumidity();

    int mq2Value = analogRead(MQ2_PIN);

    if (isnan(temperature) || isnan(humidity))
    {
        Serial.println("DHT11 Read Failed!");
    }
    else
    {
        Serial.print("Temperature: ");
        Serial.print(temperature);
        Serial.print(" °C");

        Serial.print(" | Humidity: ");
        Serial.print(humidity);
        Serial.print(" %");
    }

    Serial.print(" | MQ2: ");
    Serial.println(mq2Value);

    delay(1000);
}