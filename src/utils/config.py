# -*- coding: utf-8 -*-
import os
import yaml
from copy import deepcopy

from easydict import EasyDict
from pathlib import Path


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class SingleConfig(metaclass=SingletonMeta):
    def __init__(self, source='config-default.yaml'):
        d = EasyDict(_read_config(source=source))
        for k, v in d.items():
            setattr(self, k, v)

    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]
        else:
            raise AttributeError(name)

    def __getitem__(self, name):
        return getattr(self, name)

    def get_part(self, subconfig):
        partial_config = {} if self[subconfig] is None else deepcopy(self[subconfig])
        partial_config.update(self['general'])
        return partial_config


def _read_config(source):
    if isinstance(source, str):
        with open(source, 'r') as stream:
            config = yaml.safe_load(stream)
        if config is None:
            print(f'{source} is empty. Fill it, please.')
            exit()
    else:
        raise TypeError('Unexpected source to load config')

    working_dir = os.path.abspath(config['general']['working_dir'])
    resources_dir = os.path.abspath(config['general']['resources_dir'])
    config['general']['working_dir'] = working_dir
    _set_absolute_paths(config, working_dir, resources_dir)
    return config


def _set_absolute_paths(d, working_dir, resources_dir):
    for key in d.keys():
        if isinstance(d[key], dict):
            _set_absolute_paths(d[key], working_dir, resources_dir)
        else:
            if d[key] is not None:
                if 'path' in key:
                    d[key] = os.path.join(working_dir, d[key])
                elif 'location' in key:
                    d[key] = os.path.join(resources_dir, d[key])
