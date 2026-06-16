#pragma once

#include "esphome/core/component.h"
#include "esphome/components/climate/climate.h"
#include "esphome/components/sensor/sensor.h"
#include "esphome/components/number/number.h"
#include "esphome/components/select/select.h"
#include "esphome/components/switch/switch.h"
#include "esphome/core/log.h"
#include <cmath>

namespace esphome {
namespace innova_climate {

static const char *const TAG = "innova_climate";

class InnovaClimate : public climate::Climate, public Component {
 public:
  sensor::Sensor *sensor_temp{nullptr};
  number::Number *number_setpoint{nullptr};
  select::Select *select_mode{nullptr};
  select::Select *select_fan{nullptr};
  switch_::Switch *switch_power{nullptr};
  sensor::Sensor *sensor_status{nullptr};
  bool in_control_{false};

  void dump_config() override {
    ESP_LOGCONFIG(TAG, "Innova Climate Custom Component");
  }

  void set_sensor_temp(sensor::Sensor *s) { this->sensor_temp = s; }
  void set_number_setpoint(number::Number *n) { this->number_setpoint = n; }
  void set_select_mode(select::Select *s) { this->select_mode = s; }
  void set_select_fan(select::Select *s) { this->select_fan = s; }
  void set_switch_power(switch_::Switch *s) { this->switch_power = s; }
  void set_sensor_status(sensor::Sensor *s) { this->sensor_status = s; }

  void update_climate_state() {
    if (this->in_control_) {
      return;
    }
    bool changed = false;

    // The physical standby register bit is 1 for standby/off and 0 for on.
    // Thus, the switch state is true when fancoil is standby/off, and false when fancoil is active/on.
    // Therefore, the logical power state is the inverse of the switch state.
    bool power_state = this->switch_power ? !this->switch_power->state : true;
    std::string mode_option = (this->select_mode && this->select_mode->has_state()) ? std::string(this->select_mode->current_option()) : "None";

    ESP_LOGD(TAG, "update_climate_state: switch_power_configured=%s, switch_power_state=%s (logical_power=%s), select_mode_has_state=%s, select_mode_option=%s",
             this->switch_power ? "YES" : "NO",
             this->switch_power ? (this->switch_power->state ? "ON (standby)" : "OFF (active)") : "N/A",
             power_state ? "ON" : "OFF",
             (this->select_mode && this->select_mode->has_state()) ? "YES" : "NO",
             mode_option.c_str());

    // Handle mode state changes efficiently
    climate::ClimateMode new_mode = this->mode;
    if (this->switch_power && this->switch_power->state) { // Switch state is true -> Standby is active -> climate is OFF
      new_mode = climate::CLIMATE_MODE_OFF;
    } else if (this->select_mode && this->select_mode->has_state()) {
      std::string m = this->select_mode->current_option();
      if (m == "Heating") new_mode = climate::CLIMATE_MODE_HEAT;
      else if (m == "Cooling") new_mode = climate::CLIMATE_MODE_COOL;
      else new_mode = climate::CLIMATE_MODE_AUTO;
    }
    if (new_mode != this->mode) {
      ESP_LOGD(TAG, "Changing climate mode from %s to %s",
               climate::climate_mode_to_string(this->mode),
               climate::climate_mode_to_string(new_mode));
      this->mode = new_mode;
      changed = true;
    }

    // Handle climate action (heating, cooling, idle) based on status register
    if (new_mode == climate::CLIMATE_MODE_OFF) {
      if (this->action != climate::CLIMATE_ACTION_OFF) {
        this->action = climate::CLIMATE_ACTION_OFF;
        changed = true;
      }
    } else if (this->sensor_status && !std::isnan(this->sensor_status->state)) {
      int status = (int)this->sensor_status->state;
      climate::ClimateAction new_action = climate::CLIMATE_ACTION_IDLE;
      if (status & (1 << 0)) {
        new_action = climate::CLIMATE_ACTION_COOLING;
      } else if (status & (1 << 1)) {
        new_action = climate::CLIMATE_ACTION_HEATING;
      }
      if (this->action != new_action) {
        this->action = new_action;
        changed = true;
      }
    }

    // Handle fan mode state changes efficiently
    if (this->select_fan && this->select_fan->has_state()) {
      std::string f = this->select_fan->current_option();
      climate::ClimateFanMode new_fan = climate::CLIMATE_FAN_AUTO;
      if (f == "Night") new_fan = climate::CLIMATE_FAN_LOW;
      else if (f == "Max") new_fan = climate::CLIMATE_FAN_HIGH;
      else new_fan = climate::CLIMATE_FAN_AUTO;

      if (!this->fan_mode.has_value() || new_fan != *this->fan_mode) {
        this->fan_mode = new_fan;
        changed = true;
      }
    }

    if (changed) {
      this->publish_state();
    }
  }

  void setup() override {
    if (sensor_temp) {
      sensor_temp->add_on_state_callback([this](float state) {
        if (!std::isnan(state)) {
          // Validate temperature: values below -30C or above 80C indicate sensor fault
          float validated_temp = (state < -30.0f || state > 80.0f) ? NAN : state;
          if (this->current_temperature != validated_temp) {
            this->current_temperature = validated_temp;
            this->publish_state();
          }
        }
      });
    }

    if (number_setpoint) {
      number_setpoint->add_on_state_callback([this](float state) {
        if (this->in_control_) return;
        if (!std::isnan(state) && this->target_temperature != state) {
          this->target_temperature = state;
          this->publish_state();
        }
      });
    }

    if (switch_power) {
      switch_power->add_on_state_callback([this](bool state) { this->update_climate_state(); });
    }
    if (select_mode) {
      select_mode->add_on_state_callback([this](size_t index) { this->update_climate_state(); });
    }
    if (select_fan) {
      select_fan->add_on_state_callback([this](size_t index) { this->update_climate_state(); });
    }
    if (sensor_status) {
      sensor_status->add_on_state_callback([this](float state) { this->update_climate_state(); });
    }

    this->update_climate_state();
  }

  void control(const climate::ClimateCall &call) override {
    this->in_control_ = true;
    bool changed = false;

    if (call.get_target_temperature().has_value() && number_setpoint) {
      float target_temp = *call.get_target_temperature();
      auto num_call = number_setpoint->make_call();
      num_call.set_value(target_temp);
      num_call.perform();
      this->target_temperature = target_temp;
      number_setpoint->publish_state(target_temp);
      changed = true;
    }

    if (call.get_mode().has_value()) {
      climate::ClimateMode new_mode = *call.get_mode();
      if (new_mode == climate::CLIMATE_MODE_OFF) {
        if (switch_power) {
          switch_power->turn_on(); // Turn on standby (power OFF device)
          switch_power->publish_state(true);
        }
      } else {
        if (switch_power) {
          if (switch_power->state) {
            switch_power->turn_off(); // Turn off standby (power ON device)
          }
          switch_power->publish_state(false);
        }
        if (select_mode) {
          auto sel_call = select_mode->make_call();
          std::string opt = "Auto";
          if (new_mode == climate::CLIMATE_MODE_HEAT) opt = "Heating";
          else if (new_mode == climate::CLIMATE_MODE_COOL) opt = "Cooling";
          sel_call.set_option(opt);
          sel_call.perform();
          select_mode->publish_state(opt);
        }
      }
      this->mode = new_mode;
      changed = true;
    }

    if (call.get_fan_mode().has_value() && select_fan) {
      climate::ClimateFanMode new_fan = *call.get_fan_mode();
      auto fan_call = select_fan->make_call();
      std::string opt = "Auto";
      if (new_fan == climate::CLIMATE_FAN_LOW) opt = "Night";
      else if (new_fan == climate::CLIMATE_FAN_HIGH) opt = "Max";
      fan_call.set_option(opt);
      fan_call.perform();
      select_fan->publish_state(opt);
      this->fan_mode = new_fan;
      changed = true;
    }

    this->in_control_ = false;

    this->update_climate_state();

    if (changed) {
      this->publish_state();
    }
  }

  climate::ClimateTraits traits() override {
    auto traits = climate::ClimateTraits();
    traits.add_feature_flags(climate::CLIMATE_SUPPORTS_CURRENT_TEMPERATURE);
    traits.set_supported_modes({climate::CLIMATE_MODE_OFF, climate::CLIMATE_MODE_HEAT, climate::CLIMATE_MODE_COOL, climate::CLIMATE_MODE_AUTO});
    traits.set_supported_fan_modes({climate::CLIMATE_FAN_AUTO, climate::CLIMATE_FAN_LOW, climate::CLIMATE_FAN_HIGH});
    traits.set_visual_min_temperature(16.0);
    traits.set_visual_max_temperature(30.0);
    traits.set_visual_temperature_step(0.5);
    return traits;
  }
};

} // namespace innova_climate
} // namespace esphome
