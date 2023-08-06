"""
Module contains classes that can build configuration strings for particular controller programs.

Every controller program has to have a separate class that inherits from AbstractBuilder.
"""
import datetime
import copy

__all__ = ['Trackd']

class AbstractBuilder:
    """
    Predecessor for all builders.

    No logic/algorithm is stored here, everything is controller-dependent.
    """
    def __init__(self, baseconfig, customization):
        """
        Assigns fields.

        The overriding mechanism has to be defined when implementing particular controller configuration builder.

        :param baseconfig: Dictionary containing the base attributes that the configuration is built from
        :param customization: Dictionary that should be later applied on the base config and override certain parameters
        """
        self.base = baseconfig
        self.override = customization

    def build(self):
        """
        This is controller-specific and should always be implemented.

        :rtype: string
        """
        return ""

###

class Trackd(AbstractBuilder):
    """
    Configuration builder for the trackd program.

    http://www.mechdyne.com/trackd.aspx

    It is ready to generate two main sections, the Devices and the Connectors.
    All Devices and Connectors are properly defined with DefineDevice or DefineConnector
    and then configured with the passed attributes.
    The input dictionaries should follow this scheme:
      - parameters - To ensure the general scheme
        - devices - Dictionary of devices, every key is device's ID and should contain attributes specific for the device.
          - name - Name of the device (mandatory field)
          - parameters - Additional attributes. Some of them are treated in a special way
            - devices - The devices option assigns numerical ids to the controllers, if the attribute is not present,
              the algoritm tries to compute numerical ids, but it may result into conflicts.
            - valuators - Valuators usually represent some joysticks, the value of valuators is their quantity.
              For every valuator, only a static line is generated (i. e. 'DeviceOption EV ValuatorScale 1 1 3' for the third valuator).
              Feel free to change this behaviour (for example by extending the input parameter to a dictionary).
            Other parameters are just appended to the resulting string with no additional transformation:
            'DeviceOption deviceID attribute value'
        - connectors - Connectors are the other part of the configuration and they specify, how the application will read
          data from the devices. The input format is similar to devices, so every key is a Connector ID and the value has to contain
          following keys:
            - name - name of the connector
            - parameters - No special treatment is used this time, all parameters are just plainly transformed in the
              proper configuration format:
              'ConnectorOption connectorID attribute value'
    """
    def build(self):
        """
        Builds the configuration string.
        """
        self.derived = self._override()
        ret = ['# Config generated automatically']
        ret.append("\n# Devices")
        for device, params in self.derived['devices'].iteritems():
            ret.append( 'DefineDevice ' + device + ' ' + params['name'] )

        ret.append('')

        idx = 0
        for device, params in self.derived['devices'].iteritems():
            if 'devices' not in params['parameters']:
                ret.append( 'DeviceOption ' + device + ' devices ' + str(idx) )
            else:
                ret.append( 'DeviceOption ' + device + ' devices ' + str(params['parameters']['devices']) )

            for attr, value in params['parameters'].iteritems():
                if attr == 'devices':
                    continue
                ret.append( 'DeviceOption ' + device + ' ' + str(attr) + ' ' + str(value) )

            if 'valuators' in params['parameters']:
                for i in range(1, params['parameters']['valuators']+1): # start indexing from 1
                    ret.append( 'DeviceOption ' + device + ' ValuatorScale 1 1 ' + str(i) )

            idx += 1
            ret.append('')

        ret.append("# Connectors")
        for connector, params in self.derived['connectors'].iteritems():
            ret.append( 'DefineConnector ' + connector + ' ' + params['name'] )

        for connector, params in self.derived['connectors'].iteritems():
            for attr, value in params['parameters'].iteritems():
                ret.append( 'ConnectorOption ' + connector + ' ' + str(attr) + ' ' + str(value) )

        self.product = "\n".join(ret)
        return self.product

    def _override(self):
        """
        Method used to apply self.override to the original base configuration.

        A deepcopy of the base configuration is created if someone was to use it later.
        Then the __overrider_array_with_parameters is called for both devices and connectors
        sections.

        In addition, some possible remnants from the DB are removed from the original base configuration.
        These are _id, _rev and type keys.
        """
        notallowed = ['_id', '_rev', 'type']
        derived = copy.deepcopy(self.base['parameters'])
        derived = dict([(name, value) for name, value in derived.iteritems() if name not in notallowed])
        derived = self.__override_array_with_parameters(derived, 'devices')
        derived = self.__override_array_with_parameters(derived, 'connectors')
        return derived

    def __override_array_with_parameters(self, base, section):
        """
        Overwrites parameters in `section` in `base` with contents of the self.override dictionary.

        If self.override has the section, all its contents are checked against
        the base's section. All keys present in self.override are overriden in the base dictionary.
        Only the 'parameter' key is treated differently and overwrites all parameters in the base
        **and** adds all other parameters present in self.override.

        :return: Updated base
        """
        if section in self.override:
            for k, attrs in self.override[section].iteritems():
                if k in base[section]:
                    for attr, value in attrs.iteritems():
                        if attr == 'parameters':
                            for key, val in value.iteritems():
                                base[section][k]['parameters'][key] = val
                        else:
                            base[section][k][attr] = value
        return base


if __name__ == "__main__":
    """
    Testing ground for overriding attributes.
    """
    # Trackd
    base = {u'_rev': u'2-2cdc292f064ec954749aa1af7b2d4a68', u'controller_name': u'trackd', u'parameters': {u'devices': {u'EV': {u'name': u'event', u'parameters': {u'device': u'/dev/input/by-id/usb-Saitek_Saitek_P2900_Wireless_Pad-event-joystick 0', u'buttons': 10, u'fuzz': u'2 3 0', u'devices': u'0', u'valuators': 6}}}, u'connectors': {u'SHM2': {u'name': u'shm out 1', u'parameters': {u'data': u'controller', u'NumButtons': u'1 10', u'key': 4127, u'NumValuators': u'1 6'}}}}, u'configuration_name': u'default', u'_id': u'19c6c10a2f9feb136de7cd028600094c', u'type': u'controller'}
    override = {'connectors': {'SHM2': {'parameters': {'key': 4528}}}}
    b = Trackd(base, override)
    print(b.build())
