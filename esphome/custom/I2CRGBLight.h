#include "esphome.h"

#define I2C_SLAVE_ADDRESS 0x8

#define ON_OFF_COMMAND 0
#define SET_COLOR_COMMAND 1
#define SET_BRIGHTNESS_COMMAND 2

class I2CRGBLight : public Component, public LightOutput {
 public:
  I2CRGBLight() {
  }
  
  void setup() override {
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
    float red, green, blue;
    state->current_values_as_rgb(&red, &green, &blue);

    ESP_LOGD("I2CRGBLight", "red value is: %i", (int)(red * 255.0));
    ESP_LOGD("I2CRGBLight", "green value is: %i", (int)(green * 255.0));
    ESP_LOGD("I2CRGBLight", "blue value is: %i", (int)(blue * 255.0));

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
};