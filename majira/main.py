import os
import jira
import click
import locale
import pendulum
from majira.utils import panic


# set the locale same as the system locale, for timezone stuff
locale.setlocale(locale.LC_ALL, '')


def get_api():
    """Returns the current jira.JIRA object"""
    return click.get_current_context().obj.api


def read_config(filename):
    config = {}
    with open(filename) as fd:
        for line in fd:
            line = line.strip()
            if line.startswith('#') or not line or not '=' in line:
                continue
            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip()
            config[key] = value

    return config


class JiraClient(object):
    def __init__(self, config):
        self.username = config.get('username')
        self.password = config.get('password')
        self.url = config.get('url')
        self.timezone = pendulum.now().timezone
        self._client = None
        self.dashboards = {}

        for key in config:
            if key.startswith('list_'):
                name = key.split('_', 1)[1]
                self.dashboards[name] = config[key]

    def _validate_config(self):
        if self.username is None or self.password is None:
            return False
        return True

    @property
    def api(self):
        """Returns the jira.JIRA object for this JiraClient"""

        if self._client is None:
            if not self._validate_config():
                panic("You must configure majira first!")
            self._client = jira.JIRA(self.url, basic_auth=(self.username, self.password))
        return self._client


class MajiraError(Exception):
    pass


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.group(context_settings=CONTEXT_SETTINGS)
@click.option('--config', '-c', help="Path to the configuration file", default='~/.majirarc',
              metavar='FILENAME')
@click.pass_context
def main(ctx, config):
    config_filename = os.path.expanduser(config)
    if os.path.exists(config_filename):
        cfg_obj = read_config(config_filename)
    else:
        cfg_obj = {}

    ctx.obj = JiraClient(cfg_obj)

import majira.commands
