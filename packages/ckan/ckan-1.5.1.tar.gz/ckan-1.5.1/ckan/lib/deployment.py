# Libraries concerned with the configuration of the machine in which CKAN is
# deployed

import os
import sys
import re
import logging
from optparse import OptionParser

log = logging.getLogger(__name__)

class Machine(object):
    def os_exists(self, *args, **kwargs):
        return os.path.exists(*args, **kwargs)

    def os_listdir(self, *args, **kwargs):
        return os.listdir(*args, **kwargs)

    def open(self, *args, **kwargs):
        return open(*args, **kwargs)

DEFAULT_APACHE_CONFIG_DIR = '/etc/apache2/sites-enabled'

class CkanMachine(object):
    @classmethod
    def detect(cls, machine=None):
        '''Detect CKAN instances and return CkanMachine object'''
        ckan_instances = [] # list of dicts with keys including
                            # ckan_config_filepath and vhost

        # pass in a 'machine' so that tests can use a mock machine
        machine = machine if machine else Machine()

        apache_config = ApacheConfiguration.detect(machine=machine)
        for vhost_file in apache_config.vhost_files:
            for vhost in vhost_file.vhosts:
                # Look at the vhost WSGI script
                wsgi_script_value = vhost.get_value('WSGIScriptAlias')
                # e.g. '/ /home/dread/etc/ckan-pylons.py'
                try:
                    wsgi_script_filepath = wsgi_script_value.split(' ')[1]
                except IndexError:
                    log.error('Could not parse WSGIScriptAlias line of %s: %r',
                              vhost_file.filepath, wsgi_script_value)
                    continue
                if not machine.os_exists(wsgi_script_filepath):
                    log.error('WSGI script file %s of vhost %s does not exist',
                              wsgi_script_filepath, vhost_file.filepath)
                    continue

                wsgi_script = WsgiScript(wsgi_script_filepath, machine=machine)
                
                # By CKAN convention the CKAN config file is same filepath
                # as the WSGI, script but with .ini extension instead of .py.
                ckan_config_filepath = wsgi_script_filepath.replace('.py', '.ini')
                if not machine.os_exists(ckan_config_filepath):
                    log.error('CKAN config file %s (of vhost %s) does not exist',
                              ckan_config_filepath, vhost_file.filepath)
                    continue
                ckan_config = CkanConfig(ckan_config_filepath, machine=machine)

                ckan_instances.append({
                    'ckan_config_filepath': ckan_config_filepath,
                    'ckan_config': ckan_config,
                    'wsgi_script_filepath': wsgi_script_filepath,
                    'wsgi_script': wsgi_script,
                    'vhost_filepath': vhost_file.filepath,
                    'vhost_file': vhost_file,
                    'vhost_server_name': vhost.get_value('ServerName'),
                    'vhost': vhost,
                    })
                
        return CkanMachine(ckan_instances, machine=machine)

    def __init__(self, ckan_instances, machine=None):
        self.ckan_instances = ckan_instances

    def get_instance(self, clue):
        if not clue and len(self.ckan_instances) == 1:
            return self.ckan_instances[0]
        
        matching_instances = []
        for instance in self.ckan_instances:
            for key, value in instance.items():
                if clue == value and instance not in matching_instances:
                    matching_instances.append(instance)

        if len(matching_instances) != 1:
            assert Exception('Could not find instance: %r' % clue)

        return matching_instances[0]
        
                                  

class ApacheConfiguration(object):
    @classmethod
    def detect(cls, machine=None):
        '''Detect vhosts and return ApacheConfiguration object'''
        vhost_files = []

        machine = machine if machine else Machine()

        # get vhosts
        apache_dir = DEFAULT_APACHE_CONFIG_DIR
        enabled_files = machine.os_listdir(apache_dir)
        # NB os_listdir includes symbolic links
        for enabled_file in enabled_files:
            if enabled_file:
                enabled_filepath = os.path.join(apache_dir, enabled_file)
                vhost_file = VHostFile(enabled_filepath, machine=machine)
                vhost_files.append(vhost_file)
                
        return ApacheConfiguration(vhost_files)

    def __init__(self, vhost_files):
        self.vhost_files = vhost_files

        self.vhosts = []
        for vhost_file in self.vhost_files:
            self.vhosts.extend(vhost_file.vhosts)

    def __str__(self):
        s = 'CKAN Apache Configurations:\n'
        for vhost_file in self.vhost_files:
            s += 'Config file: %s\n' % vhost_file.filepath
            for vhost in vhost_file.vhosts:
                name = vhost.get_value('ServerName')
                s += ' VHost: name=%s\n' % name
        return s

    def get_vhost(self, clue):
        matching_vhosts = []
        for vhost in self.vhosts:
            if clue == vhost.filepath or \
                   clue == vhost.get_value('ServerName'):
                matching_vhosts.append(vhost)

        if len(matching_vhosts) != 1:
            assert Exception('Could not find vhost: %r' % clue)

        return matching_vhosts[0]
        
                
class VHostFile(object):
    def __init__(self, filepath, machine=None):
        self.filepath = filepath
        self.vhosts = []
        self.unfinished_vhost = []
        self.machine = machine if machine else Machine()

        include_re = re.compile('\s*Include\s*(.*)\s*')

        f = self.machine.open(filepath, 'r')
        # NB 'open' follows symbolic links transparently
        lines = []
        line = f.readline()
        while line != '':
            include_re_match = include_re.match(line)
            if include_re_match:
                include_filepath = include_re_match.groups()[0]
                included_vhost_file = VHostFile(include_filepath, machine)
                assert len(included_vhost_file.vhosts) == 0, included_vhost_file.vhosts
                assert included_vhost_file.unfinished_vhost
                lines.extend(included_vhost_file.unfinished_vhost.lines)
            else:
                lines.append(line.rstrip())
            if '</VirtualHost>' in line:
                self.vhosts.append(VHost(lines, filepath))
                lines = []
            line = f.readline()
        if lines:
            self.unfinished_vhost = VHost(lines, filepath)

class VHost(object):
    def __init__(self, lines, filepath=None):
        self.lines = lines
        self.filepath = filepath
        
        key_value_matcher = re.compile('^\s*([^\s]*)\s*(.*)$')
        self.key_values = {}
        for line in lines:
            match = key_value_matcher.match(line)
            if match:
                key, value = match.groups()
                self.key_values[key] = value

    def get_value(self, key, default=None):
        return self.key_values.get(key, default)

    def __str__(self):
        return '%s:\n' % self.filepath + '\n'.join(self.lines)

class WsgiScript(object):
    def __init__(self, filepath, machine=None):
        self.filepath = filepath
        self.lines = []
        self.machine = machine if machine else Machine()

        f = self.machine.open(filepath, 'r')
        line = f.readline()
        while line != '':
            self.lines.append(line.rstrip())
            line = f.readline()

    def __str__(self):
        return '%s:\n' % self.filepath + '\n'.join(self.lines)
    
class CkanConfig(object):
    class ConfigSection(dict):
        start_line = None
        finish_line = None
    
    def __init__(self, filepath, machine=None):
        self.filepath = filepath
        self.machine = machine if machine else Machine()
        self.lines = [] # config content, line by line
        self.section_dicts = {} # config content in dicts by section

        section_heading_re = re.compile('\s*\[(.*?)\]\s*\n')
        key_value_re = re.compile('\s*([^#].*?)\s*=\s*(.*?)\s*\n')

        f = self.machine.open(filepath, 'r')
        section_heading = None
        line = f.readline()
        line_number = 0
        while line != '':
            self.lines.append(line.rstrip())
            line_number += 1
            section_heading_match = section_heading_re.match(line)
            if section_heading_match:
                if section_heading:
                    self.section_dicts[section_heading].finish_line = line_number
                section_heading = section_heading_match.groups()[0]
                self.section_dicts[section_heading] = self.ConfigSection()
                self.section_dicts[section_heading].start_line = line_number
            else:
                key_value_match = key_value_re.match(line)
                if key_value_match:
                    key, value = key_value_match.groups()
                    sh = str(section_heading)
                    self.section_dicts[sh][key] = value
            line = f.readline()
        if section_heading:
            self.section_dicts[section_heading].finish_line = line_number
    

usage = '''%prog [OPTIONS] COMMAND [--help]
Commands:
    apache
    vhost
    config'''
def command():
    parser = OptionParser(usage=usage)
##    parser.add_option("-k", "--destination-ckan-api-key", dest="destination_ckan_api_key",
##                      help="Destination CKAN's API key", metavar="API-KEY")
##    parser.add_option("-g", "--group-name", dest="group_name",
##                      help="Destination CKAN group's name")
##    parser.add_option("-t", "--group-title", dest="group_title",
##                      help="Destination CKAN group's title")
##    parser.add_option("-s", "--site-name", dest="site_name",
##                      help="Name of source CKAN site - so source can be tagged")

    (options, args) = parser.parse_args()

    try:
        assert (not len(args) < 1), 'Command was not supplied'
    except AssertionError, e:
        print 'ERROR: ', e
        parser.print_help()
        sys.exit(1)
    command = args[0]

    logging.basicConfig(level=logging.INFO)

    if command == 'apache':
        assert (not len(args) > 1), 'Extra argument(s) not recognised: %r' % args[1:]
        apache = ApacheConfiguration.detect()
        print apache
    elif command == 'vhost':
        apache = ApacheConfiguration.detect()
        if len(apache.vhosts) == 1:
            vhost = apache.vhosts[0]
        else:
            assert (not len(args) < 2), 'Please supply the vhost filepath / ServerName'
            vhost = apache.get_vhost(args[1])
        assert (not len(args) > 2), 'Extra argument(s) not recognised: %r' % args[1:]
        print vhost
    elif command == 'config':
        ckan = CkanMachine.detect()
        if len(ckan.ckan_instances) == 1:
            ckan_instance = ckan.ckan_instances[0]
        else:
            assert (not len(args) < 2), 'Please supply the config filepath / ServerName. Choice: %r' % ckan.ckan_instances
            ckan_instance = ckan.get_instance(args[1])
        assert (not len(args) > 2), 'Extra argument(s) not recognised: %r' % args[1:]
        print ckan_instance
    else:
        print 'Command %r not understood' % command
    
if __name__ == '__main__':
    command()

