# Copyright 2011 Andrew Fort. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""Module for managing shard of Notch Agents for the client."""

import logging
import os
import pprint
import re

import jsonrpclib

import yaml

import lb_transport


class Error(Exception):
    pass


class NoAgentsError(Error):
    """No agent addresses were passed to the client."""


class AgentShardManager(object):
    """Manages a sharded collection of Notch Agents for the client.

    In a distributed environment, not only does one desire load-balancing
    between agents, but one needs to be able to select which shard (group)
    of agents should be used for a particular request.

    This manager allows the client to be able to select the agent shard based
    on a key in a shard map, which is normally a regular expression matched
    against the request's device_name field.
    """

    USER_FN = '.notchrc'
    SITE_FN = 'notchrc'
    SITE_DIR = '/etc'

    # TODO(afort): Add an LRU to improve lookup performance

    def __init__(self, load_balancing_policy, use_ssl=False, path='/JSONRPC2'):
        self._map = {}
        self._lb_policy = load_balancing_policy
        if use_ssl:
            self._protocol = 'https://'
        else:
            self._protocol = 'http://'
        self.path = path
        # Have a default shard (for non sharded requests or environments)
        self._default_shard = None
        # Record the last shard used
        self._last_shard = None

    def __str__(self):
        result = {}
        result.update(self._map)
        result['__default__'] = self._default_shard
        result['__last__'] = self._last_shard
        return pprint.pformat(result)

    def setup(self, agents=None):
        """Setup the manager, using either the shard map or local overrides."""
        agents = agents or os.getenv('NOTCH_AGENTS')
        self._setup_shard_map()
        if agents:
            self._setup_agents(agents)

        if not self._default_shard and not self._map:
            raise NoAgentsError('No Notch agents supplied to Client.')
        elif not self._default_shard and self._map:
            for key in self._map:
                self._default_shard = self._map[key]
                break

    def shard_for_device(self, device_name):
        """Returns the best shard for a particular device name."""
        if device_name is not None:
            for regex, value in self._map.iteritems():
                if isinstance(regex, str):
                    # Skip the __default__ entry.
                    continue
                match = regex.match(device_name)
                if match is not None:
                    self._last_shard = self._map.get(regex)
                    return value
        if self._default_shard is not None:
            return self._default_shard
        elif self._last_shard is not None:
            return self._last_shard
        else:
            raise NoAgentsError(
                'No shard could be found for device %s' % device_name)

    def _setup_agents(self, agents):
        if isinstance(agents, str):
            agents = self._text_to_list(agents)
            if agents:
                self._use_default_agents(agents)
        else:
            agents = self._clean_list(agents)
            if agents:
                self._use_default_agents(agents)

    def _setup_shard_map(self):
        shard_file_name = self._detect_shard_map_file()
        if shard_file_name:
            self._load_shard_map_file(shard_file_name)
            return

    def _setup_shards(self, data):
        """Sets up the Agent shards based on the supplied shard data dict."""
        for key, value in data.iteritems():
            if key.strip().lower() == '__default__':
                self._use_default_agents(self._text_to_list(value),
                                         only_default_agents=False)
            else:
                regex = re.compile(key, re.I)
                hosts = self._text_to_list(value)
                if hosts:
                    self._map[regex] = self._create_shard(hosts)

    def _load_shard_map_file(self, filename):
        try:
            f = open(filename)
            config = yaml.load(f)
            f.close()
            # PyYAML may return a string if the file doesn't
            # parse as Yaml.  Empty files return None.
            if config is None or isinstance(config, str):
                config = {}
            if not config:
                logging.error(
                    'Error loading config. '
                    'File %r did not have valid YAML contents.', filename)
            else:
                # Detect "shard" key in combined config file.
                if isinstance(config.get('shards'), dict):
                    config = config['shards']
                # Test the format slightly
                for k, v in config.iteritems():
                    if not isinstance(v, (str, unicode)):
                        logging.error('Error parsing config file %r', filename)
                        config = {}
                        break
        except (OSError, IOError, yaml.error.YAMLError), e:
            logging.error('%s: %s', e.__class__.__name__, str(e))
            config = {}
        if config:
            logging.debug(
                'Found shard config, loading contents. Data: %r', config)
        self._setup_shards(config)

    def _text_to_list(self, agents):
        result = []
        if agents.strip():
            for agent in agents.split(','):
                result.append(agent.strip())
        return result

    def _clean_list(self, agent_list):
        result = []
        for agent in agent_list:
            if agent.strip():
                result.append(agent.strip())
        return result

    def _use_default_agents(self, agents, only_default_agents=True):
        self._default_shard = self._create_shard(agents)
        if only_default_agents:
            self._map = {}

    def _detect_shard_map_file(self):
        result = None
        home_dir = os.getenv('HOME')
        if home_dir is not None:
            for path in (os.path.join(home_dir, self.USER_FN),
                         os.path.join(self.SITE_DIR, self.SITE_FN)):
                if os.path.exists(path):
                    result = path
        logging.debug('Detected shard map file %r', result)
        return result

    def _create_shard(self, agents):
        transport = lb_transport.LoadBalancingTransport(
            hosts=agents,
            transport=jsonrpclib.jsonrpc.Transport,
            policy=self._lb_policy)
        notch = jsonrpclib.Server(
            self._protocol + self.path, transport=transport)
        return notch, transport

