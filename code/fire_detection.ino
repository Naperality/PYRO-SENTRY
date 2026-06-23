#include <DHT.h>
#include <SoftwareSerial.h>

#define DHTPIN 2
#define DHTTYPE DHT11
#define MQ2_PIN A0

DHT dht(DHTPIN, DHTTYPE);

// SIM800L
SoftwareSerial sim800(7, 8);

// Thresholds
const float TEMP_THRESHOLD = 40.0;
const int MQ2_THRESHOLD = 500;

// Anti-spam
bool alertSent = false;

// Last AI Status
bool aiFireDetected = false;

void setup()
{
    Serial.begin(9600);

    dht.begin();

    sim800.begin(9600);

    Serial.println("PyroSentry Started");

    delay(3000);
}

void loop()
{
    // Read sensors
    float temperature = dht.readTemperature();
    int smokeValue = analogRead(MQ2_PIN);

    // Receive AI message
    if (Serial.available())
    {
        String command = Serial.readStringUntil('\n');
        command.trim();

        if (command == "FIRE")
        {
            aiFireDetected = true;
            Serial.println("AI FIRE RECEIVED");
        }
        else if (command == "SAFE")
        {
            aiFireDetected = false;
            Serial.println("AI SAFE RECEIVED");
        }
    }

    Serial.print("Temp: ");
    Serial.print(temperature);

    Serial.print(" MQ2: ");
    Serial.print(smokeValue);

    Serial.print(" AI: ");
    Serial.println(aiFireDetected);

    bool sensorFire =
        (temperature >= TEMP_THRESHOLD) &&
        (smokeValue >= MQ2_THRESHOLD);

    bool confirmedFire =
        aiFireDetected &&
        sensorFire;

    if (confirmedFire && !alertSent)
    {
        Serial.println("CONFIRMED FIRE");

        sendSMS(temperature, smokeValue);

        alertSent = true;
    }

    if (!confirmedFire)
    {
        alertSent = false;
    }

    delay(1000);
}

void sendSMS(float temp, int smoke)
{
    sim800.println("AT+CMGF=1");
    delay(1000);

    sim800.println("AT+CMGS=\"+639XXXXXXXXX\"");
    delay(1000);

    sim800.println("PYROSENTRY ALERT");
    sim800.println("");
    sim800.println("CONFIRMED FIRE DETECTED");

    sim800.print("Temperature: ");
    sim800.print(temp);
    sim800.println(" C");

    sim800.print("Smoke: ");
    sim800.println(smoke);

    sim800.println("");
    sim800.println("Immediate inspection required.");

    delay(1000);

    sim800.write(26);

    Serial.println("SMS SENT");
}