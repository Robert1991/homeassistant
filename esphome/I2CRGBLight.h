#include "esphome.h"

#define I2C_SLAVE_ADDRESS 0x8

#define ON_OFF_COMMAND 0
#define SET_COLOR_COMMAND 1
#define SET_BRIGHTNESS_COMMAND 2

#define SDA_PIN 5
#define SCL_PIN 4

class I2CRGBLight : public Component, public LightOutput {
 public:
  void setup() override {
    establishI2CConnectionTo(SDA_PIN, SCL_PIN, true);

    sendI2CCommandWithParameter(I2C_SLAVE_ADDRESS,
                                ON_OFF_COMMAND, 1);
    sendI2CCommandWithParameter(I2C_SLAVE_ADDRESS,
                                SET_BRIGHTNESS_COMMAND,
                                255);
  }
  LightTraits get_traits() override {
    auto traits = LightTraits();
    traits.set_supports_brightness(true);
    traits.set_supports_rgb(true);
    traits.set_supports_rgb_white_value(false);
    traits.set_supports_color_temperature(false);
    return traits;
  }

  void write_state(LightState *state) override {
    if (checkI2CConnection(SDA_PIN, SCL_PIN)) {
      establishI2CConnectionTo(SDA_PIN, SCL_PIN, false);
    }

    float red, green, blue;
    state->current_values_as_rgb(&red, &green, &blue);

    ESP_LOGI("I2CRGBLight", "red value is: %i", (int)(red * 255.0));
    ESP_LOGI("I2CRGBLight", "green value is: %i", (int)(green * 255.0));
    ESP_LOGI("I2CRGBLight", "blue value is: %i", (int)(blue * 255.0));

    int red_value = (int) (red * 255.0);
    int green_value = (int)(green * 255.0);
    int blue_value = (int)(blue * 255.0);

    Wire.beginTransmission(I2C_SLAVE_ADDRESS);
    Wire.write(SET_COLOR_COMMAND);
    Wire.write(red_value);
    Wire.write(green_value);
    Wire.write(blue_value);
    Wire.endTransmission();
  }

  void sendI2CCommandWithParameter(int secondaryAddress, int command, int parameter)
  {
      Wire.beginTransmission(secondaryAddress);
      Wire.write(command);
      Wire.write(parameter);
      Wire.endTransmission();
  }

  bool checkI2CConnection(int sdaPin, int sclPin)
  {
    bool connectionWasLost = false;
    pinMode(sdaPin, INPUT);
    pinMode(sclPin, INPUT);
    if (digitalRead(sdaPin) != 1)
    {
      ESP_LOGI("I2CRGBLight", "SDA pin is low");
      connectionWasLost = true;
    }
    if (digitalRead(sclPin) != 1)
    {
      ESP_LOGI("I2CRGBLight", "SCL pin is low");
      connectionWasLost = true;
    }
    return connectionWasLost;
  }

  void establishI2CConnectionTo(int sdaPort, int sclPort, bool startupDelay)
  {
    int rtn = clearI2CBus(sdaPort, sclPort, startupDelay);
    if (rtn != 0)
    {
      ESP_LOGI("I2CRGBLight", "I2C bus error. Could not clear");
      if (rtn == 1)
      {
        ESP_LOGI("I2CRGBLight", "SCL clock line held low");
      }
      else if (rtn == 2)
      {
        ESP_LOGI("I2CRGBLight", "SCL clock line held low by slave clock stretch");
      }
      else if (rtn == 3)
      {
        ESP_LOGI("I2CRGBLight", "SDA data line held low");
      }
    }
    else
    {
      Wire.begin(sdaPort, sclPort);
      ESP_LOGI("I2CRGBLight", "Wire connection successfully established on: {SDA : %i , SCL : %i }", sdaPort, sclPort);
    }
  }

  int clearI2CBus(int sdaPin, int sclPin, bool startupDelay)
  {
#if defined(TWCR) && defined(TWEN)
    TWCR &= ~(_BV(TWEN)); // Disable the Atmel 2-Wire interface so we can control the SDA and SCL pins directly
#endif

    pinMode(sdaPin, INPUT_PULLUP); // Make SDA (data) and SCL (clock) pins Inputs with pullup.
    pinMode(sclPin, INPUT_PULLUP);

    if (startupDelay)
    {
      delay(2500); // Wait 2.5 secs. This is strictly only necessary on the first power
      // up of the DS3231 module to allow it to initialize properly,
      // but is also assists in reliable programming of FioV3 boards as it gives the
      // IDE a chance to start uploaded the program
      // before existing sketch confuses the IDE by sending Serial data.
    }

    boolean sclPinIsLow = (digitalRead(sclPin) == LOW); // Check is SCL is Low.
    if (sclPinIsLow)
    {           // If it is held low Arduno cannot become the I2C master.
      return 1; // I2C bus error. Could not clear SCL clock line held low
    }

    boolean sdaPinIsLow = (digitalRead(sdaPin) == LOW); // vi. Check SDA input.
    int clockCount = 20;                                // > 2x9 clock

    while (sdaPinIsLow && (clockCount > 0))
    { //  vii. If SDA is Low,
      clockCount--;
      // Note: I2C bus is open collector so do NOT drive SCL or SDA high.
      pinMode(sclPin, INPUT);        // release SCL pullup so that when made output it will be LOW
      pinMode(sclPin, OUTPUT);       // then clock SCL Low
      delayMicroseconds(10);         //  for >5uS
      pinMode(sclPin, INPUT);        // release SCL LOW
      pinMode(sclPin, INPUT_PULLUP); // turn on pullup resistors again
      // do not force high as slave may be holding it low for clock stretching.
      delayMicroseconds(10); //  for >5uS
      // The >5uS is so that even the slowest I2C devices are handled.
      sclPinIsLow = (digitalRead(sclPin) == LOW); // Check if SCL is Low.
      int counter = 20;
      while (sclPinIsLow && (counter > 0))
      { //  loop waiting for SCL to become High only wait 2sec.
        counter--;
        delay(100);
        sclPinIsLow = (digitalRead(sclPin) == LOW);
      }
      if (sclPinIsLow)
      {           // still low after 2 sec error
        return 2; // I2C bus error. Could not clear. SCL clock line held low by slave clock stretch for >2sec
      }
      sdaPinIsLow = (digitalRead(sdaPin) == LOW); //   and check SDA input again and loop
    }
    if (sdaPinIsLow)
    {           // still low
      return 3; // I2C bus error. Could not clear. SDA data line held low
    }

    // else pull SDA line low for Start or Repeated Start
    pinMode(sdaPin, INPUT);  // remove pullup.
    pinMode(sdaPin, OUTPUT); // and then make it LOW i.e. send an I2C Start or Repeated start control.
    // When there is only one I2C master a Start or Repeat Start has the same function as a Stop and clears the
    // bus.
    /// A Repeat Start is a Start occurring after a Start with no intervening Stop.
    delayMicroseconds(10);         // wait >5uS
    pinMode(sdaPin, INPUT);        // remove output low
    pinMode(sdaPin, INPUT_PULLUP); // and make SDA high i.e. send I2C STOP control.
    delayMicroseconds(10);         // x. wait >5uS
    pinMode(sdaPin, INPUT);        // and reset pins as tri-state inputs which is the default state on reset
    pinMode(sclPin, INPUT);
    return 0; // all ok
  }

};