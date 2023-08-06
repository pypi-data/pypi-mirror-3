#!/usr/bin/env python

"""
unified configuration with serialization/deserialization
"""

import copy
import os
import sys
import optparse

# imports for configuration providers
try:
    import json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        json = None
try:
    import yaml
except ImportError:
    yaml = None

__all__ = ['Configuration',
           'configuration_providers',
           'types',
           'UnknownOptionException',
           'MissingValueException',
           'ConfigurationProviderException',
           'TypeCastException',
           'ConfigurationOption']

### exceptions

class UnknownOptionException(Exception):
    """exception raised when a non-configuration value is present in the configuration"""

class MissingValueException(Exception):
    """exception raised when a required value is missing"""

class ConfigurationProviderException(Exception):
    """exception raised when a configuration provider is missing, etc"""

class TypeCastException(Exception):
    """exception raised when a configuration item cannot be coerced to a type"""


### configuration providers for serialization/deserialization

configuration_providers = []

class ConfigurationProvider(object):
    """
    abstract base class for configuration providers for
    serialization/deserialization
    """
    def read(self, filename):
        raise NotImplementedError("Abstract base class")

    def write(self, config, filename):
        if isinstance(filename, basestring):
            f = file(filename, 'w')
            newfile = True
        else:
            f = filename
            newfile = False
        try:
            self._write(f, config)
        finally:
            # XXX try: finally: works in python >= 2.5
            if newfile:
                f.close()
    def _write(self, fp, config):
        raise NotImplementedError("Abstract base class")

if json:
    class JSON(ConfigurationProvider):
        indent = 2
        extensions = ['json']
        def read(self, filename):
            return json.loads(file(filename).read())
        def _write(self, fp, config):
            fp.write(json.dumps(config, indent=self.indent, sort_keys=True))
            # TODO: could use templates to get order down, etc
    configuration_providers.append(JSON())

if yaml:
    class YAML(ConfigurationProvider):
        extensions = ['yml', 'yaml']
        def read(self, filename):
            f = file(filename)
            config = yaml.load(f)
            f.close()
            return config
        def _write(self, fp, config):
            fp.write(yaml.dump(config))
            # TODO: could use templates to get order down, etc

    configuration_providers.append(YAML())

# TODO: add a configuration provider for taking command-line arguments
# from a file

__all__.extend([i.__class__.__name__ for i in configuration_providers])

### optparse interface

class ConfigurationOption(optparse.Option):
    """option that keeps track if it is seen"""
    # TODO: this should be configurable or something
    def take_action(self, action, dest, opt, value, values, parser):
        optparse.Option.take_action(self, action, dest, opt, value, values, parser)

        # add the parsed option to the set of things parsed
        if not hasattr(parser, 'parsed'):
            parser.parsed = set()
        parser.parsed.add(dest)

        # switch on types
        formatter = getattr(parser, 'cli_formatter')
        if formatter:
            formatter = formatter(dest)
            setattr(values, dest, formatter(getattr(values, dest)))

### plugins for option types
### TODO: this could use a bit of thought
### They should probably be classes
# class Option(object):
#     def arguments(self, name, value):
#         """return arguments appropriate for construction of an optparse.Option
#     def take_action(self, ...):
#         """do something appropriate based on type"""

class BaseCLI(object):
    """base_cli for all option types"""

    def __call__(self, name, value):
        """return args, kwargs needed to instantiate an optparse option"""

        args = value.get('flags', ['--%s' % name])
        if not args:
            # No CLI interface
            return (), {}

        kw = {'dest': name}
        help = value.get('help', name)
        if 'default' in value:
            kw['default'] = value['default']
            help += ' [DEFAULT: %s]' % value['default']
        kw['help'] = help
        kw['action'] = 'store'
        return args, kw

    def take_action(self, value):
        return value

class BoolCLI(BaseCLI):

    def __call__(self, name, value):

        # preserve the default values
        help = value.get('help')
        flags = value.get('flags')

        args, kw = BaseCLI.__call__(self, name, value)
        kw['help'] = help # reset
        if value.get('default'):
            kw['action'] = 'store_false'
            if not flags:
                args = ['--no-%s' % name]
            if not help:
                kw['help'] = 'disable %s' % name
        else:
            kw['action'] = 'store_true'
            if not help:
                kw['help'] = 'enable %s' % name
        return args, kw

class ListCLI(BaseCLI):

    def __call__(self, name, value):
        args, kw = BaseCLI.__call__(self, name, value)

        # TODO: could use 'extend'
        # - http://hg.mozilla.org/build/mozharness/file/5f44ba08f4be/mozharness/base/config.py#l41

        # TODO: what about nested types?
        kw['action'] = 'append'
        return args, kw

class IntCLI(BaseCLI):

    def __call__(self, name, value):
        args, kw = BaseCLI.__call__(self, name, value)
        kw['type'] = 'int'
        return args, kw

class FloatCLI(BaseCLI):

    def __call__(self, name, value):
        args, kw = BaseCLI.__call__(self, name, value)
        kw['type'] = 'float'
        return args, kw

class DictCLI(ListCLI):

    delimeter = '='

    def take_action(self, value):
        bad = [i for i in value if self.delimeter not in i]
        if bad:
            raise AssertionError("Each value must be delimited by '%s': %s" % (self.delimeter, bad))
        return dict([i.split(self.delimeter, 1) for i in value])

# TODO: 'dict'-type cli interface

types = {bool:  BoolCLI(),
         int:   IntCLI(),
         float: FloatCLI(),
         list:  ListCLI(),
         dict:  DictCLI(),
         None:  BaseCLI()} # default

__all__ += [i.__class__.__name__ for i in types.values()]

class Configuration(optparse.OptionParser):
    """declarative configuration object"""

    options = {} # configuration basis

    def __init__(self, configuration_providers=configuration_providers, types=types, load=None, dump='--dump', **parser_args):

        # setup configuration
        self.config = {}
        self.configuration_providers = configuration_providers
        self.types = types

        # setup optionparser
        if 'description' not in parser_args:
            parser_args['description'] = getattr(self, '__doc__', '')
            if 'formatter' not in parser_args:
                class PlainDescriptionFormatter(optparse.IndentedHelpFormatter):
                    """description formatter for console script entry point"""
                    def format_description(self, description):
                        if description:
                            return description.strip() + '\n'
                        else:
                            return ''
                parser_args['formatter'] = PlainDescriptionFormatter()
        parser_args.setdefault('option_class', ConfigurationOption)
        optparse.OptionParser.__init__(self, **parser_args)
        self.parsed = set()
        self.optparse_options(self)
        # add option(s) for configuration_providers
        if load:
            self.add_option(load,
                            dest='load', action='append',
                            help="load configuration from a file")

        # add an option for dumping
        formats = self.formats()
        if formats and dump:
            self.add_option(dump, dest='dump',
                            help="dump configuration to a file; Formats: %s" % formats)


    ### methods for iteration
    ### TODO: make the class a real iterator

    def items(self):
        # TODO: allow options to be a list of 2-tuples
        return self.options.items()

    ### methods for validating configuration

    def check(self, config):
        """
        check validity of configuration to be added
        """

        # ensure options in configuration are in self.options
        unknown_options = [i for i in config if i not in self.options]
        if unknown_options:
            raise UnknownOptionException("Unknown options: %s" % ', '.join(unknown_options))

        # ensure options are of the right type (if specified)
        for key, value in config.items():
            _type = self.options[key].get('type')
            if _type is None and 'default' in self.options[key]:
                _type = type(self.options[key]['default'])
            if _type is not None and not isinstance(value, _type):
                try:
                    config[key] = _type(value)
                except BaseException, e:
                    raise TypeCastException("Could not coerce %s, %s, to type %s: %s" % (key, value, _type.__name__, e))

        return config

    def validate(self):
        """validate resultant configuration"""

        for key, value in self.items():
            if key not in self.config:
                required = value.get('required')
                if required:
                    if isinstance(required, basestring):
                        required_message = required
                    else:
                        required_message = "Parameter %s is required but not present" % key
                    # TODO: this should probably raise all missing values vs
                    # one by one
                    raise MissingValueException(required_message)
        # TODO: configuration should be locked after this is called

    ### methods for adding configuration

    def __call__(self, *args):
        """add items to configuration and check it"""

        for config in args:
            self.add(config)

        # add defaults if not present
        for key, value in self.items():
            if 'default' in value and key not in self.config:
                self.config[key] = value['default']

        # validate total configuration
        self.validate()
        # TODO: configuration should be locked after this is called

    def add(self, config, check=True):
        """update configuration: not undoable"""

        self.check(config) # check config to be added
        self.config.update(config)
        # TODO: option to extend; augment lists/dicts

    ### methods for optparse
    ### XXX could go in a subclass

    def cli_formatter(self, option):
        handler = self.types[self.options[option].get('type')]
        return getattr(handler, 'take_action', lambda x: 1)

    def optparse_options(self, parser):
        """add optparse options to a OptionParser instance"""
        for key, value in self.items():
            handler = self.types[value.get('type')]
            args, kw = handler(key, value)
            if not args:
                # No CLI interface
                continue
            parser.add_option(*args, **kw)

    def parse_args(self, *args, **kw):

        self.parsed = set()
        options, args = optparse.OptionParser.parse_args(self, *args, **kw)

        # get CLI configuration options
        cli_config = dict([(key, value) for key, value in options.__dict__.items()
                           if key in self.options and key in self.parsed])

        # deserialize configuration
        configuration_files = getattr(options, 'load', args)
        missing = [i for i in configuration_files
                   if not os.path.exists(i)]
        if missing:
            self.error("Missing files: %s" % ', '.join(missing))
        config = []
        for f in configuration_files:
            try:
                config.append(self.deserialize(f))
            except BaseException, e:
                parser.error(str(e))
        config.append(cli_config)

        missingvalues = None
        try:
            # generate configuration
            self(*config)
        except MissingValueException, missingvalues:
            pass

        # dump configuration, if specified
        dump = getattr(options, 'dump')
        if dump:
            # TODO: have a way of specifying format other than filename
            self.serialize(dump)

        if missingvalues and not dump:
            # XXX assuming if you don't have values you were just dumping
            raise missingvalues

        # update options from config
        options.__dict__.update(self.config)

        # return parsed arguments
        return options, args

    ### serialization/deserialization

    def formats(self):
        """formats for deserialization"""
        retval = []
        for provider in self.configuration_providers:
            if provider.extensions and hasattr(provider, 'write'):
                retval.append(provider.extensions[0])
        return retval

    def configuration_provider(self, format):
        """configuration provider guess for a given filename"""
        for provider in self.configuration_providers:
            if format in provider.extensions:
                return provider

    def filename2format(self, filename):
        extension = os.path.splitext(filename)[-1]
        return extension.lstrip('.') or None

    def serialize(self, filename, format=None, full=False):
        """
        serialize configuration to a file
        - filename: path of file to serialize to
        - format: format of configuration provider
        - full: whether to serialize non-set optional strings [TODO]
        """
        # TODO: allow file object vs file name

        if not format:
            format = self.filename2format(filename)
            if not format:
                raise Exception('Please specify a format')
                # TODO: more specific exception type

        provider = self.configuration_provider(format)
        if not provider:
            raise Exception("Provider not found for format: %s" % format)

        config = copy.deepcopy(self.config)

        provider.write(config, filename)

    def deserialize(self, filename, format=None):
        """load configuration from a file"""
        # TODO: allow file object vs file name

        assert os.path.exists(filename)

        # get the format
        if not format:
            format = self.filename2format(filename)

        # get the providers in some sensible order
        providers = self.configuration_providers[:]
        if format:
            providers.sort(key=lambda x: int(format in x.extensions), reverse=True)

        # deserialize the data
        for provider in providers:
            try:
                return provider.read(filename)
            except:
                continue
        else:
            raise ConfigurationProviderException("Could not load %s" % filename)
