import collections
import copy
import os
import re
import string
import yaml
from rock.exceptions import ConfigError


PARENT_RE = re.compile(r'\{\{\s*parent\s*\}\}', re.MULTILINE)
TEMPLATE_RE = re.compile(r'^(?:build|clean|run|test)(?:_.+)?$')


class Config(collections.Mapping):

    MOUNT = '/'
    DATA = os.path.join(os.path.dirname(__file__), 'data')

    def __init__(self, data):
        self._data = data
        self._setup = False

    def parse(self, path, require_exists=True, require_parses=True):
        if not os.path.isfile(path):
            if require_exists:
                raise ConfigError('not found: ' + path)
            else:
                return None
        try:
            with open(path) as f:
                return yaml.load(f)
        except Exception, error:
            if require_parses:
                raise ConfigError('parse error: ' + path)

    def merge(self, src, dst):
        if src is None:
            return dst
        if 'env' in src:
            # ensure env is a dict of strings
            if (not isinstance(src['env'], dict) or
                not all(map(lambda v: isinstance(v, basestring),
                        src['env'].values()))):
                raise ConfigError('env must be an associative array of ' +
                                  'strings')
            # evaluate env variables
            for name, value in src['env'].items():
                dst['env'][name] = string.Template(
                    src['env'][name]).safe_substitute(**dst['env'])
            del src['env']
        # parent tag to build, clean, run and test
        for name in src.keys():
            if not TEMPLATE_RE.match(name):
                continue
            if name not in dst:
                if isinstance(src[name], basestring):
                    src[name] = PARENT_RE.sub('', src[name])
                elif isinstance(src[name], dict):
                    for subname in src[name]:
                        value = src[name][subname]
                        if isinstance(value, basestring):
                            src[name][subname] = PARENT_RE.sub('', value)
                dst[name] = src[name]
            elif isinstance(src[name], basestring):
                if not isinstance(dst[name], basestring):
                    raise ConfigError('unable to merge "%s" into "str"' %
                                      type(dst[name]).__name__)
                dst[name] = PARENT_RE.sub(dst[name], src[name])
            elif isinstance(src[name], dict):
                dst_is_dict = isinstance(dst[name], dict)
                for subname in src[name]:
                    if isinstance(dst[name], basestring):
                        src[name][subname] = PARENT_RE.sub(dst[name],
                                                           src[name][subname])
                    elif dst_is_dict:
                        if subname in dst[name]:
                            src[name][subname] = PARENT_RE.sub(
                                dst[name][subname],
                                src[name][subname],
                            )
                            del dst[name][subname]
                        else:
                            src[name][subname] = PARENT_RE.sub(
                                '',
                                src[name][subname],
                            )
                if dst_is_dict:
                    src[name].update(dst[name])
                dst[name] = src[name]
            del src[name]
        dst.update(src)

    def setup(self):
        if self._setup:
            return
        self._setup = True
        # setup configuration
        data = {}
        # runtime
        yml_path = ('path' in self._data and
                    os.path.join(self._data['path'], '.rock.yml'))
        if yml_path and os.path.isfile(yml_path):
            data = self.parse(yml_path)
            if not isinstance(data, dict):
                raise ConfigError('.rock.yml syntax error')
            data.update(self._data)
        else:
            data = copy.deepcopy(self._data)
        if 'runtime' in data and 'runtime_type' not in data:
            data['runtime_type'] = data['runtime'].rstrip('0123456789')
        # project
        for name in ('path', 'runtime', 'runtime_type'):
            if name not in data:
                raise ConfigError('%s is required' % name)
        # paths
        runtime_path = os.path.join(self.MOUNT, 'opt', 'rock', 'runtime',
                                    data['runtime'])
        etc_path = os.path.join(self.MOUNT, 'etc', 'rock', 'runtime')
        runtime_type_yml = data['runtime_type'] + '.yml'
        runtime_yml = data['runtime'] + '.yml'
        # ensure runtime exists
        if not os.path.isdir(runtime_path):
            raise ConfigError("runtime path doesn't exist")
        # configs
        runtime_config = self.parse(os.path.join(runtime_path,
                                    'rock.yml'))
        rock_type_config = self.parse(os.path.join(self.DATA, 'runtime',
                                      runtime_type_yml), require_exists=False)
        rock_config = self.parse(os.path.join(self.DATA, 'runtime',
                                 runtime_yml), require_exists=False)
        etc_type_config = self.parse(os.path.join(etc_path,
                                     runtime_type_yml), require_exists=False)
        etc_config = self.parse(os.path.join(etc_path, runtime_yml),
                                require_exists=False)
        # merge
        self._data = {
            'env': {
                'PROJECT_PATH': data['path'],
            },
        }
        # merge runtime
        self.merge(runtime_config, self._data)
        # merge runtime config
        if rock_config or etc_config:
            self.merge(rock_config, self._data)
            self.merge(etc_config, self._data)
        else:
            self.merge(rock_type_config, self._data)
            self.merge(etc_type_config, self._data)
        # merge project
        self.merge(data, self._data)

    def __contains__(self, *args, **kwargs):
        self.setup()
        return self._data.__contains__(*args, **kwargs)

    def __getitem__(self, *args, **kwargs):
        self.setup()
        return self._data.__getitem__(*args, **kwargs)

    def __iter__(self, *args, **kwargs):
        self.setup()
        return self._data.__iter__(*args, **kwargs)

    def __len__(self, *args, **kwargs):
        self.setup()
        return self._data.__len__(*args, **kwargs)
