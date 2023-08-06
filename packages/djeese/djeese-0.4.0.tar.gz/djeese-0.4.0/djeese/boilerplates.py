# -*- coding: utf-8 -*-
from djeese.smartconfig import SmartConfig
import os

REQUIRED_BOILERPLATE_KEYS = ['name', 'author', 'author-url', 'url', 'version',
                             'description', 'license', 'license-path']
EXTRA_BOILERPLATE_KEYS = ['settings']

REQUIRED_SETTINGS_KEYS = ['name', 'verbose-name', 'type']
EXTRA_SETTINGS_KEYS = ['default']

VALID_TYPES = ['string', 'stringtuplelist', 'stringlist', 'boolean', 'integer', 'choices']

def validate_boilerplate(config, printer, validate_templates=True):
    valid = True
    if 'boilerplate' not in config:
        printer.error("Section 'boilerplate' not found")
        valid = False
    else:
        if not validate_boilerplate_section(config, printer):
            valid = False
    if 'templates' not in config:
        printer.error("Section 'templates' not found")
        valid = False
    elif validate_templates:
        if not validate_template_section(config, printer):
            valid = False
    settings = config['app'].getlist('settings')
    for setting in settings:
        if not validate_settings_section(config, printer, setting):
            valid = False
    if valid:
        printer.always("Configuration valid")
    else:
        printer.always("Configuration invalid")
    return valid

def validate_template_section(config, printer):
    valid = True
    templates = config['templates'].as_dict()
    for template in templates.keys():
        if not os.path.exists(os.path.join('templates', template)):
            printer.error("Template %r not found" % template)
            valid = False
    return valid

def validate_boilerplate_section(config, printer):
    valid = True
    printer.info("Required section 'boilerplate' found")
    boilerplate = config['boilerplate']
    for required in REQUIRED_BOILERPLATE_KEYS:
        if required not in boilerplate:
            printer.error("Option '%s' not found in 'boilerplate' section" % required)
            valid = False
        else:
            printer.info("Required option '%s' found in 'boilerplate' section" % required)
    return valid

def validate_settings_section(config, printer, setting):
    valid = True
    if setting not in config:
        printer.error("Could not find settings section %r" % setting)
        return False
    setting_config = config[setting]
    for required in REQUIRED_SETTINGS_KEYS:
        if required not in setting_config:
            printer.error("Could not find required option %r in settings section %r" % (required, setting))
            valid = False
    if 'type' in setting_config:
        typevalue = setting_config['type']
        if typevalue not in VALID_TYPES:
            valid_types = ', '.join(VALID_TYPES)
            printer.error("Setting %r type %r is not valid. Valid choices: %s" % (setting, typevalue, valid_types))
            valid = False
        if typevalue == 'choices':
            choices = setting_config['choices']
            if choices not in config:
                printer.error("Choices section %r not found." % (choices))
                valid = False
    if valid:
        printer.info("Settings section valid")
    return valid


class BoilerplateConfiguration(SmartConfig):
    def validate(self, validate_templates=True):
        """
        Validate this configuration
        """
        return validate_boilerplate(self, self.printer, validate_templates)
