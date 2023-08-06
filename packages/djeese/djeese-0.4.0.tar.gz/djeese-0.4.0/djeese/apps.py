# -*- coding: utf-8 -*-
from __future__ import with_statement
from djeese.smartconfig import SmartConfig
from djeese.utils import check_urls
import os


VALID_TYPES = ['string', 'stringtuplelist', 'stringlist', 'boolean', 'integer']
REQUIRED_APP_KEYS = ['name', 'packagename', 'installed-apps', 'description',
                     'license', 'url', 'version', 'private']
DEPRECATION_APP_KEYS = {
    'license-text': 'license-path',
}
EXTRA_APP_KEYS = ['settings', 'author', 'author-url', 'translation-url',
                  'plugins', 'apphooks']
REQUIRED_SETTINGS_KEYS = ['name', 'verbose-name', 'type']
EXTRA_SETTINGS_KEYS = ['default', 'required', 'editable']

def validate_app(config, validate_templates, printer):
    """
    Validate an app (AppConfiguration instance) and print errors using the
    printer (djeese.utils.Printer instance).
    """
    valid = True
    if 'app' not in config:
        printer.error("Section 'app' not found")
        valid = False
    else:
        if not validate_app_section(config, printer):
            valid = False
    if 'templates' in config and validate_templates:
        if not validate_templates_section(config, printer):
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

def validate_app_section(config, printer):
    """
    Validate the [app] section of an app configuration
    """
    valid = True
    printer.info("Required section 'app' found")
    app = config['app']
    for required in REQUIRED_APP_KEYS:
        if required not in app:
            printer.error("Option '%s' not found in 'app' section" % required)
            valid = False
        else:
            printer.info("Required option '%s' found in 'app' section" % required)
    for old, new in DEPRECATION_APP_KEYS.items():
        if old not in app and new not in app:
            printer.error("Option '%s' not found in 'app' section" % new)
            valid = False
        elif old in app:
            printer.warning("Option '%s' in 'app' section is deprecated, use '%s' instead" % (old, new)) 
    return valid

def validate_templates_section(config, printer):
    """
    Validate the [templates] section of an app configuration
    """
    valid = True
    templates = config['templates'].as_dict()
    reverse_templates = dict([(v,k) for k,v in templates.items()])
    urls = []
    paths = []
    for path in templates.values():
        if path.startswith(('http://', 'https://')):
            printer.warning("Template loading from URLs is deprecated.")
            urls.append(path)
        else:
            paths.append(path)
    if urls:
        responses = check_urls(urls)
        for url, success in responses:
            name = reverse_templates[url]
            if not success:
                printer.error("Could not load template %r from %r" % (name, url))
                valid = False
            else:
                printer.info("Successfully loaded %r from %r" % (name, url))
    for path in paths:
        if not os.path.exists(path):
            printer.warning("Template '%s' not found" % path)
            valid = False
    return valid

def validate_settings_section(config, printer, setting):
    """
    Validate the settings section of an app configuration for a setting
    """
    valid = True
    if setting not in config:
        printer.error("Could not find settings section %r" % setting)
        return False
    setting_config = config[setting]
    for required in ['verbose-name', 'name', 'type']:
        if required not in setting_config:
            printer.error("Could not find required option %r in settings section %r" % (required, setting))
            valid = False
    if 'type' in setting_config:
        typevalue = setting_config['type']
        if typevalue not in VALID_TYPES:
            valid_types = ', '.join(VALID_TYPES)
            printer.error("Setting %r type %r is not valid. Valid choices: %s" % (setting, typevalue, valid_types))
    printer.info("Settings section valid")
    return valid


class AppConfiguration(SmartConfig):
    def validate(self, validate_templates=True):
        """
        Validate this configuration
        """
        return validate_app(self, validate_templates, self.printer)
