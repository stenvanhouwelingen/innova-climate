import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import climate, sensor, number, select, switch
from esphome.const import CONF_ID

innova_climate_ns = cg.esphome_ns.namespace("innova_climate")
InnovaClimate = innova_climate_ns.class_("InnovaClimate", cg.Component, climate.Climate)

DEPENDENCIES = ["climate", "sensor", "number", "select", "switch"]

CONF_SENSOR_TEMP = "sensor_temp"
CONF_NUMBER_SETPOINT = "number_setpoint"
CONF_SELECT_MODE = "select_mode"
CONF_SELECT_FAN = "select_fan"
CONF_SWITCH_POWER = "switch_power"
CONF_SENSOR_STATUS = "sensor_status"

CONFIG_SCHEMA = climate.climate_schema(InnovaClimate).extend({
    cv.Required(CONF_SENSOR_TEMP): cv.use_id(sensor.Sensor),
    cv.Required(CONF_NUMBER_SETPOINT): cv.use_id(number.Number),
    cv.Required(CONF_SELECT_MODE): cv.use_id(select.Select),
    cv.Required(CONF_SELECT_FAN): cv.use_id(select.Select),
    cv.Required(CONF_SWITCH_POWER): cv.use_id(switch.Switch),
    cv.Optional(CONF_SENSOR_STATUS): cv.use_id(sensor.Sensor),
}).extend(cv.COMPONENT_SCHEMA)

async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    await climate.register_climate(var, config)

    sens = await cg.get_variable(config[CONF_SENSOR_TEMP])
    cg.add(var.set_sensor_temp(sens))

    num = await cg.get_variable(config[CONF_NUMBER_SETPOINT])
    cg.add(var.set_number_setpoint(num))

    sel_mode = await cg.get_variable(config[CONF_SELECT_MODE])
    cg.add(var.set_select_mode(sel_mode))

    sel_fan = await cg.get_variable(config[CONF_SELECT_FAN])
    cg.add(var.set_select_fan(sel_fan))

    sw = await cg.get_variable(config[CONF_SWITCH_POWER])
    cg.add(var.set_switch_power(sw))

    if CONF_SENSOR_STATUS in config:
        sens_status = await cg.get_variable(config[CONF_SENSOR_STATUS])
        cg.add(var.set_sensor_status(sens_status))
