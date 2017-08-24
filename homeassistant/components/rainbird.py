import homeassistant.helpers as helpers
import logging


REQUIREMENTS = ['pyrainbird==0.0.7']

# Home Assistant Setup
DOMAIN = 'rainbird'
SERVER = ''
PASSWORD = ''
STATE_VAR = 'rainbird.activestation'

_LOGGER = logging.getLogger(__name__)


def setup(hass, config):

    server = config[DOMAIN].get('stickip')
    password = config[DOMAIN].get('password')

    # RainbirdSetup
    from pyrainbird import RainbirdController

    controller = RainbirdController(_LOGGER)
    controller.setConfig(server, password)
    _LOGGER.info("Rainbird Controller setup to " + str(server))

    def startirrigation(call):
        station_id = call.data.get('station')
        duration = call.data.get('duration')
        _LOGGER.info("Requesting irrigation for " +
                     str(station_id) + " duration " + str(duration))
        result = controller.startIrrigation(station_id, duration)
        if (result == 1):
            _LOGGER.info("Irrigation started on " + str(station_id) +
                         " for " + str(duration))
        elif (result == 0):
            _LOGGER.error("Error sending request")
        else:
            _LOGGER.error("Request was not acknowledged!")

    def stopirrigation(call):
        _LOGGER.info("Stop request irrigation")
        result = controller.stopIrrigation()
        if (result == 1):
            _LOGGER.info("Stopped irrigation")
            print("Success")
        elif (result == 0):
            _LOGGER.error("Error sending request")
        else:
            _LOGGER.error("Request was not acknowledged!")

    def getirrigation():
        _LOGGER.info("Request irrigation state")
        result = controller.currentIrrigation()
        if (result < 0):
            _LOGGER.error("Error sending request")
            return -1

        return result
    initialstatus = getirrigation()
    hass.states.set(STATE_VAR, initialstatus)

    hass.services.register(DOMAIN, 'start_irrigation', startirrigation)
    hass.services.register(DOMAIN, 'stop_irrigation', stopirrigation)

    helpers.event.track_time_change(
            hass, lambda _: hass.states.set(STATE_VAR, getirrigation()),
            year=None, month=None, day=None,
            hour=None, minute=None, second=[00, 30]
    )
    _LOGGER.info("Initialized Rainbird Controller")

    return True
