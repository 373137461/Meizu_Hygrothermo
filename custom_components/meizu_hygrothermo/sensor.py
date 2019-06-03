import re
import logging
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from datetime import timedelta
from homeassistant.const import (ATTR_BATTERY_LEVEL,CONF_HOST, CONF_NAME, CONF_MAC, CONF_SCAN_INTERVAL, TEMP_CELSIUS)
from homeassistant.helpers.entity import Entity
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.helpers.event import track_time_interval
from homeassistant.util.dt import utcnow
import socket
import json
REQUIREMENTS = []

_LOGGER = logging.getLogger(__name__)

BT_MAC = vol.All(
    cv.string,
    vol.Length(min=17, max=17)
)

SCAN_INTERVAL = timedelta(seconds=30)
NAME = "Meijia BT Hygrothermograph"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_MAC, default=None): vol.Any(BT_MAC, None),
    vol.Required(CONF_HOST, default=None): cv.string,
    vol.Optional(CONF_NAME, default=NAME): cv.string,
    vol.Optional(CONF_SCAN_INTERVAL, default=SCAN_INTERVAL): cv.time_period,
})

SENSOR_TYPES = {
    'Temperature': [TEMP_CELSIUS, 'mdi:thermometer'],
    'Humidity': ['%', 'mdi:water-percent']
}

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the sensor platform."""
    device = MeizuHygroThermo(hass, config.get(CONF_NAME), config.get(CONF_HOST),config.get(CONF_MAC))
    add_devices(device.entities)
    track_time_interval(hass, device.get_data, config.get(CONF_SCAN_INTERVAL))

class MeizuHygroThermoDelegate(object):
    def __init__(self):
        self.temperature = None
        self.humidity = None
        self.received = False

    def handleNotification(self, cHandle, data):
        if cHandle == 14:
            m = re.search('T=([\d\.]*)\s+?H=([\d\.]*)', ''.join(map(chr, data)))
            self.temperature = m.group(1)
            self.humidity = m.group(2)
            self.received = True

class MeizuHygroThermo(object):
    def __init__(self, hass, name, address,mac):
        self.address = mac
        self.host = address
        self.battery = None
        self.temperature = None
        self.humidity = None
        self.last_battery = None

        self.entities = [
            MeizuHygroThermoEntity(hass, name, 'Temperature'),
            MeizuHygroThermoEntity(hass, name, 'Humidity')
        ]

        self.get_data()

    def get_data(self, now = None):
        try:
            c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            HOST=self.host
            PORT=21567
            BUFSIZ=1024
            ADDR=(HOST,PORT)
            c.connect(ADDR)
            c.send(self.address.encode())
            data = c.recv(BUFSIZ)
            print(data.decode('utf-8'))
            c.close()
            json_str = json.loads(data.decode('utf-8'))
            print(json_str)
            self.temperature = json_str['temperature']
            self.humidity = json_str['humidity']
            self.battery = json_str['battery']
            self.last_battery = "1"
            ok = True
        except Exception as ex:
            _LOGGER.error("Unexpected error: {}".format(ex))
            ok = False

        for i in [0, 1]:
            changed = self.entities[i].set_state(ok, self.battery, self.temperature if i == 0 else self.humidity)
            if (not now is None) and changed:
                self.entities[i].async_schedule_update_ha_state()

class MeizuHygroThermoEntity(Entity):
    def __init__(self, hass, name, device_type):
        self.hass = hass
        self._name = '{} {}'.format(name, device_type)
        self._state = None
        self._is_available = True
        self._type = device_type
        self._device_state_attributes = {}
        self.__errcnt = 0
        self.__laststate = None

    @property
    def name(self):
        """Return the name of the device."""
        return self._name

    @property
    def available(self):
        """Return True if entity is available."""
        return self._is_available

    @property
    def should_poll(self):
        """Return the polling state. No polling needed."""
        return False

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return self._device_state_attributes

    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        try:
            return SENSOR_TYPES.get(self._type)[1]
        except TypeError:
            return None

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        try:
            return SENSOR_TYPES.get(self._type)[0]
        except TypeError:
            return None

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    def set_state(self, is_available, battery, state_value):
        changed = False
        if is_available:
            if not battery is None:
                self._device_state_attributes[ATTR_BATTERY_LEVEL] = battery
                changed = True
            self._state = state_value
            changed = changed or self.__laststate != state_value
            self.__laststate = state_value
            self.__errcnt = 0
            self._is_available = True
        else:
            self.__errcnt += 1

        if self.__errcnt > 3:
            self._is_available = False
            changed = True
        
        return changed
