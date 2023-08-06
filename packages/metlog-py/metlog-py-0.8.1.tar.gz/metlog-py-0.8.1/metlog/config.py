# ***** BEGIN LICENSE BLOCK *****
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Contributor(s):
#   Rob Miller (rmiller@mozilla.com)
#   Victor Ng (vng@mozilla.com)
#
# ***** END LICENSE BLOCK *****
"""
This module provides helpers to handle configuration details as well
as providing some late binding helper objects which can be used to
hook into plugin systems.

"""
from metlog.client import MetlogClient
from metlog.exceptions import EnvironmentNotFoundError
from metlog.path import DottedNameResolver
from textwrap import dedent
import ConfigParser
import StringIO
import os
import re

_IS_INTEGER = re.compile('^-?[0-9].*')
_IS_ENV_VAR = re.compile('\$\{(\w.*)?\}')


def _get_env_val(match_obj):
    var = match_obj.groups()[0]
    if var not in os.environ:
        raise EnvironmentNotFoundError(var)
    return os.environ[var]


def _convert(value):
    """Converts a config value. Numeric integer strings are converted to
    integer values.  'True-ish' string values are converted to boolean True,
    'False-ish' to boolean False. Any alphanumeric (plus underscore) value
    enclosed within ${dollar_sign_curly_braces} is assumed to represent an
    environment variable, and will be converted to the corresponding value
    provided by os.environ.
    """
    def do_convert(value):
        if not isinstance(value, basestring):
            # we only convert strings
            return value

        value = value.strip()
        if _IS_INTEGER.match(value):
            try:
                return int(value)
            except ValueError:
                pass
        elif value.lower() in ('true', 't', 'on', 'yes'):
            return True
        elif value.lower() in ('false', 'f', 'off', 'no'):
            return False
        match_obj = _IS_ENV_VAR.match(value)
        if match_obj:
            return _get_env_val(match_obj)
        return value

    if isinstance(value, basestring) and '\n' in value:
        return [line for line in [do_convert(line)
                                  for line in value.split('\n')]
                if line.strip() != '']

    return do_convert(value)


def client_from_dict_config(config):
    """
    Configure a metlog client, fully configured w/ sender and extensions.

    :param config: Configuration dictionary.

    The configuration dict supports the following values:

    :logger: Metlog client default logger value.
    :severity: Metlog client default severity value.
    :disabled_timers: Sequence of string tokens identifying timers that are to
                      be deactivated.
    :sender: Nested dictionary containing sender configuration.
    :extensions: Nested dictionary specifying dynamic methods to be added to
                 the instantiated Metlog client.

    All of the configuration values are optional, but failure to include a
    sender may result in a non-functional Metlog client. Any unrecognized keys
    will be ignored.

    The sender configuration supports the following values:

    :class: (required) Dotted name identifying the sender class to instantiate.
    :args: Sequence of non-keyword args to pass to sender constructor.
    :<kwargs>: All remaining key-value pairs in the sender config dict will be
               passed as keyword arguments to the sender constructor.

    The extensions dictionary keys should be the attribute name to use for each
    dynamic method. The values should be the dotted name resolving to the
    function to be used.
    """
    logger = config.get('logger', '')
    severity = config.get('severity', 6)
    disabled_timers = config.get('disabled_timers', [])

    sender_config = config.get('sender', {})
    extensions = config.get('extensions', {})

    resolver = DottedNameResolver()
    sender_clsname = sender_config.pop('class')
    sender_cls = resolver.resolve(sender_clsname)
    sender_args = sender_config.pop('args', tuple())
    sender = sender_cls(*sender_args, **sender_config)

    client = MetlogClient(sender, logger, severity, disabled_timers)

    for name, func_name in extensions.items():
        func = resolver.resolve(func_name)
        client.add_method(name, func)

    return client


def client_from_stream_config(stream, section):
    """
    Extract configuration data in INI format from a stream object (e.g. a file
    object) and use it to generate a Metlog client. Config values will be sent
    through the _convert function for possible type conversion.

    :param stream: Stream object containing config information.
    :param section: INI file section containing the configuration we care
                    about.

    Note that all sender config options should be prefaced by "sender_", e.g.
    "sender_class" should specify the dotted name of the sender class to use.
    Similarly all extension method settings should be prefaced by
    "extensions_".
    """
    config = ConfigParser.SafeConfigParser()
    config.readfp(stream)
    client = {}
    sender = {}
    extensions = {}
    for opt in config.options(section):
        value = _convert(config.get(section, opt))
        if opt.startswith('sender_'):
            sender[opt[len('sender_'):]] = value
        elif opt.startswith('extensions_'):
            extensions[opt[len('extensions_'):]] = value
        else:
            client[opt] = value
    if sender:
        client['sender'] = sender
    if extensions:
        client['extensions'] = extensions
    return client_from_dict_config(client)


def client_from_text_config(text, section):
    """
    Extract configuration data in INI format from provided text and use it to
    generate a Metlog client. Text is converted to a stream and passed on to
    `client_from_stream_config`.

    :param text: INI text containing config information.
    :param section: INI file section containing the configuration we care
                    about.
    """
    stream = StringIO.StringIO(dedent(text))
    return client_from_stream_config(stream, section)
