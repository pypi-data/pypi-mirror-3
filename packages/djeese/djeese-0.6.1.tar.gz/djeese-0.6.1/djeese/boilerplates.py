# -*- coding: utf-8 -*-
from djeese.smartconfig import SmartConfig
import os

REQUIRED_BOILERPLATE_KEYS = ['name', 'author', 'author-url', 'url', 'version',
                             'description', 'license', 'license-path']

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


class BoilerplateConfiguration(SmartConfig):
    def validate(self, validate_templates=True):
        """
        Validate this configuration
        """
        return validate_boilerplate(self, self.printer, validate_templates)
