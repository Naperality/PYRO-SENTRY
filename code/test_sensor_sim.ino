#include <DHT.h>
#include <SoftwareSerial.h>

// --------------------
// DHT11 Setup
// --------------------
#define DHTPIN 2
#define DHTTYPE DHT11

DHT dht(DHTPIN, DHTTYPE);

// --------------------
// MQ2 Setup
// --------------------
#define MQ2_PIN A0

// --------------------
// SIM800L Setup
// --------------------
SoftwareSerial sim800(7, 8); // RX, TX

// --------------------
// Thresholds
// --------------------
const float TEMP_THRESHOLD = 40.0;
const int SMOKE_THRESHOLD = 400;

// Prevent SMS spam
bool alertSent = false;

void setup()
{
    Serial.begin(9600);

    dht.begin();

    sim800.begin(9600);

    Serial.println("PyroSentry Sensor Test Starting...");

    delay(3000);

    sim800.println("AT");
    delay(1000);

    while(sim800.available())
    {
        Serial.write(sim800.read());
    }
}

void loop()
{
    float temperature = dht.readTemperature();
    float humidity = dht.readHumidity();

    int smokeValue = analogRead(MQ2_PIN);

    Serial.print("Temp: ");
    Serial.print(temperature);
    Serial.print(" C");

    Serial.print(" | Humidity: ");
    Serial.print(humidity);
    Serial.print("%");

    Serial.print(" | MQ2: ");
    Serial.println(smokeValue);

    bool fireCondition =
        (temperature >= TEMP_THRESHOLD) ||
        (smokeValue >= SMOKE_THRESHOLD);

    if (fireCondition && !alertSent)
    {
        Serial.println("FIRE CONDITION DETECTED!");
        sendSMS(temperature, smokeValue);
        alertSent = true;
    }

    // Reset alarm when conditions return to normal
    if (!fireCondition)
    {
        alertSent = false;
    }

    delay(2000);
}

void sendSMS(float temp, int smoke)
{
    Serial.println("Sending SMS...");

    sim800.println("AT+CMGF=1");
    delay(1000);

    // CHANGE TO YOUR NUMBER
    sim800.println("AT+CMGS=\"+639XXXXXXXXX\"");
    delay(1000);

    sim800.println("PyroSentry Alert!");
    sim800.print("Temperature: ");
    sim800.print(temp);
    sim800.println(" C");

    sim800.print("Smoke Level: ");
    sim800.println(smoke);

    sim800.println("Possible Fire Detected!");

    delay(500);

    sim800.write(26); // CTRL+Z

    Serial.println("SMS Sent");
}