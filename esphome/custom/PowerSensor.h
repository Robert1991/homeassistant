#include "esphome.h"

const int NUMBER_OF_DATAPOINTS = 15;

class FloatingAverage
{
private:
  float readings[NUMBER_OF_DATAPOINTS];
  int currentIndex = 0;
  float total = 0;

public:
  float floatingAverage(float nextValue)
  {
    float average;
    total = total - readings[currentIndex];
    readings[currentIndex] = nextValue;
    total = total + readings[currentIndex];
    currentIndex = currentIndex + 1;
    if (currentIndex >= NUMBER_OF_DATAPOINTS)
    {
      currentIndex = 0;
    }
    average = total / NUMBER_OF_DATAPOINTS;
    return average;
  }
};

class PowerSensor : public Sensor, public Component
{
public:
  float VOLTAGE_SOURCE = 230;
  float AMPS_PER_100_MV = 100;
  int MULTIPLEXER_FACTOR = 3;

  int currentMillis = 0;
  int sampleCurrentMillis = 0;
  float avgVoltage = 0.0;
  FloatingAverage *voltageFloatingAvg = new FloatingAverage();

  float errorInAmps;
  ads1115::ADS1115Sensor *powerSensor;
  std::string sensorName;

  PowerSensor(std::string sensorName, float errorInAmps)
  {
    this->sensorName = sensorName;
    this->errorInAmps = errorInAmps;
  }

  void setup() override
  {
    currentMillis = millis();
    sampleCurrentMillis = millis();
    powerSensor = aquireSensorReferenceFromApp();
  }

  void loop() override
  {
    if ((millis() - sampleCurrentMillis) > 1500)
    {
      float voltageInMV = sampleSensorValueInMV();
      avgVoltage = voltageFloatingAvg->floatingAverage(voltageInMV);
      if ((millis() - currentMillis) > 10000)
      {
        float voltageRMS = avgVoltage * 0.707;
        float ampsRMS = (voltageRMS / AMPS_PER_100_MV) - errorInAmps;
        if (ampsRMS < 0.0)
        {
          ampsRMS = 0.0;
        }
        ESP_LOGI("power sensor", "read amps rms %f A from %s", ampsRMS, sensorName.c_str());

        float power = (ampsRMS * VOLTAGE_SOURCE) / MULTIPLEXER_FACTOR;
        ESP_LOGI("power sensor", "read power %f W from %s", power, sensorName.c_str());

        publish_state(round(power));
        this->currentMillis = millis();
      }
      sampleCurrentMillis = millis();
    }
  }

  float sampleSensorValueInMV()
  {
    int currentSampleMillis = millis();
    float maxValue = 0.0;
    float minValue = 6.114;
    while ((millis() - currentSampleMillis) < 500)
    {
      float lastSample = powerSensor->sample();
      if (lastSample > maxValue)
      {
        maxValue = lastSample;
      }

      if (lastSample < minValue)
      {
        minValue = lastSample;
      }
    }
    return ((maxValue - minValue) / 2) * 1000;
  }

  ads1115::ADS1115Sensor *aquireSensorReferenceFromApp()
  {
    auto sensors = App.get_sensors();
    for (auto *obj : sensors)
    {
      auto sensorName = obj->get_name();
      if (sensorName.compare(this->sensorName) == 0)
      {
        return static_cast<ads1115::ADS1115Sensor *>(obj);
      }
    }
    return nullptr;
  }
};
