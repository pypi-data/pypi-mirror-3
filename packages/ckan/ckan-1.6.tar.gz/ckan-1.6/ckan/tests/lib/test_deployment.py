import os

from nose.tools import assert_equal

from ckan.lib.deployment import (VHost, VHostFile, ApacheConfiguration,
                                 CkanMachine, WsgiScript, CkanConfig)

def get_sample_dir():
    sample_dir = os.path.join(os.path.dirname(__file__), 'samples')
    assert os.path.exists(sample_dir)
    return sample_dir

class MockMachine(object):
    '''Mimics a machine\'s filesystem, making it easy to test.'''
    def __init__(self, file_dict):
        self.file_dict = file_dict
        
    def open(self, filename, *args, **kwargs):
        class TstFile(object):
            def __init__(self, buf):
                self.lines = buf.split('\n')
                self.current_line = 0
                
            def readline(self):
                try:
                    line = self.lines[self.current_line] + '\n'
                except IndexError:
                    return ''
                self.current_line += 1
                return line

        file_buf = self.file_dict[filename]
        return TstFile(file_buf)

    def os_listdir(self, dir, *args, **kwargs):
        files = []
        for filepath in self.file_dict:
            if filepath.startswith(dir):
                files.append(filepath)
        return files

    def os_exists(self, filepath, *args, **kwargs):
        return filepath in self.file_dict

class TestVHost:
    def test_basic(self):
        lines = '''<VirtualHost *:80>
        ServerName datagm.ckan.net
        ServerAlias www.datagm.org.uk datagm.org.uk datagm.test.ckan.net

        WSGIScriptAlias / /home/dread/etc/ckan-pylons.py

        # pass authorization info on (needed for rest api)
        WSGIPassAuthorization On

        ErrorLog /var/log/apache2/ckan.net.error.log
        CustomLog /var/log/apache2/ckan.net.custom.log combined
</VirtualHost>
'''.split('\n')
        vhost = VHost(lines)
        assert_equal(vhost.get_value('WSGIScriptAlias'), '/ /home/dread/etc/ckan-pylons.py')
        assert_equal(vhost.get_value('ErrorLog'), '/var/log/apache2/ckan.net.error.log')
        assert_equal(vhost.get_value('ServerAlias'), 'www.datagm.org.uk datagm.org.uk datagm.test.ckan.net')

        
class TestVHostFile:
    def test_basic_using_real_vhost_file(self):
        filename = os.path.join(get_sample_dir(), 'vhost1.txt')
        vhost_file = VHostFile(filename)
        assert len(vhost_file.vhosts) == 1, vhost_file.vhosts
        vhost = vhost_file.vhosts[0]
        assert_equal(vhost.get_value('WSGIScriptAlias'), '/ /home/dread/etc/ckan-pylons.py')
        assert_equal(vhost.get_value('ServerAlias'), '127.0.1.1')
        assert_equal(vhost.get_value('ServerName'), '127.0.0.1')
        
    def test_basic(self):
        mock_machine = MockMachine({
            'vhost1.txt': '''
<VirtualHost *:80>
        ServerAlias 127.0.1.1
        ServerName 127.0.0.1

        WSGIScriptAlias / /home/dread/etc/ckan-pylons.py

        # pass authorization info on (needed for rest api)
        WSGIPassAuthorization On

        ErrorLog /var/log/apache2/ckan.net.error.log
        CustomLog /var/log/apache2/ckan.net.custom.log combined
</VirtualHost>
'''
            })
        filename = 'vhost1.txt'
        vhost_file = VHostFile(filename, machine=mock_machine)
        assert len(vhost_file.vhosts) == 1, vhost_file.vhosts
        vhost = vhost_file.vhosts[0]
        assert_equal(vhost.get_value('WSGIScriptAlias'), '/ /home/dread/etc/ckan-pylons.py')
        
    def test_include(self):
        mock_machine = MockMachine({
            '/etc/apache2/sites-enabled/datagm': '''
<VirtualHost *:80>
    Include /etc/apache2/sites-available/datagm.common
</VirtualHost>''',
            '/etc/apache2/sites-available/datagm.common': '''
    DocumentRoot /var/lib/ckan/datagm/static
    ServerName datagm.ckan.net
    ServerAlias www.datagm.org.uk datagm.org.uk datagm.test.ckan.net

    WSGIScriptAlias / /etc/ckan/datagm/datagm.py
'''
            })
        filename = '/etc/apache2/sites-enabled/datagm'
        vhost_file = VHostFile(filename, machine=mock_machine)
        assert len(vhost_file.vhosts) == 1, vhost_file.vhosts
        vhost = vhost_file.vhosts[0]
        assert_equal(vhost.get_value('WSGIScriptAlias'), '/ /etc/ckan/datagm/datagm.py')

class TestApacheConfiguration:
    def test_basic(self):
        mock_machine = MockMachine({
            '/etc/apache2/sites-enabled/site1': '''
<VirtualHost *:80>
        ServerName site1
        WSGIScriptAlias / /home/dread/etc/ckan-pylons1.py
</VirtualHost>
''',
            '/etc/apache2/sites-enabled/site2': '''
<VirtualHost *:80>
        ServerName site2
        WSGIScriptAlias / /home/dread/etc/ckan-pylons2.py
</VirtualHost>
'''
            })
        apache_config = ApacheConfiguration.detect(machine=mock_machine)
        assert len(apache_config.vhost_files) == 2, vhost_file.vhosts
        assert_equal(apache_config.vhost_files[0].filepath,
                     '/etc/apache2/sites-enabled/site1')
        assert_equal(apache_config.vhost_files[1].filepath,
                     '/etc/apache2/sites-enabled/site2')
        assert len(apache_config.vhosts) == 2, vhost_file.vhosts
        assert_equal(apache_config.vhosts[0].get_value('WSGIScriptAlias'), '/ /home/dread/etc/ckan-pylons1.py')
        assert_equal(apache_config.vhosts[1].get_value('WSGIScriptAlias'), '/ /home/dread/etc/ckan-pylons2.py')
        assert_equal(apache_config.get_vhost('site1').filepath,
                     '/etc/apache2/sites-enabled/site1')
        assert_equal(apache_config.get_vhost('/etc/apache2/sites-enabled/site2').filepath,
                     '/etc/apache2/sites-enabled/site2')
        
class TestCkanMachine:
    def test_basic(self):
        mock_machine = MockMachine({
            '/etc/apache2/sites-enabled/norway': '''
<VirtualHost *:80>
        ServerName no.ckan.net
        WSGIScriptAlias / /home/dread/etc/norway/norway.py
</VirtualHost>
''',
            '/etc/apache2/sites-enabled/spain': '''
<VirtualHost *:80>
        WSGIScriptAlias / /home/dread/etc/spain/spain.py
</VirtualHost>
''',
            '/home/dread/etc/norway/norway.py': '',
            '/home/dread/etc/norway/norway.ini': '''
[DEFAULT]
debug = true

[app:main]
ckan.plugins = stats
''',
            '/home/dread/etc/spain/spain.py': '',
            '/home/dread/etc/spain/spain.ini': '',
            })
        
        ckan_machine = CkanMachine.detect(machine=mock_machine)
        assert len(ckan_machine.ckan_instances) == 2, ckan_machine.ckan_instances
        norway = ckan_machine.ckan_instances[0]
        assert_equal(norway['ckan_config_filepath'],
                     '/home/dread/etc/norway/norway.ini')
        assert isinstance(norway['vhost'], VHost), vhost
        assert_equal(norway['vhost_filepath'],
                     '/etc/apache2/sites-enabled/norway')
        assert isinstance(norway['wsgi_script'], WsgiScript), norway['wsgi_script']
        assert_equal(norway['wsgi_script_filepath'],
                     '/home/dread/etc/norway/norway.py')
        assert_equal(norway['ckan_config_filepath'],
                     '/home/dread/etc/norway/norway.ini')
        assert isinstance(norway['ckan_config'], CkanConfig), norway['ckan_config']
        
        spain = ckan_machine.ckan_instances[1]
        assert_equal(spain['ckan_config_filepath'],
                     '/home/dread/etc/spain/spain.ini')

        assert_equal(ckan_machine.get_instance('/home/dread/etc/spain/spain.ini')['ckan_config_filepath'],
                     '/home/dread/etc/spain/spain.ini')
        assert_equal(ckan_machine.get_instance('no.ckan.net')['ckan_config_filepath'],
                     '/home/dread/etc/norway/norway.ini')
            
    def test_only_one_instance(self):
        mock_machine = MockMachine({
            '/etc/apache2/sites-enabled/norway': '''
<VirtualHost *:80>
        ServerName no.ckan.net
        WSGIScriptAlias / /home/dread/etc/norway/norway.py
</VirtualHost>
''',
            '/home/dread/etc/norway/norway.py': '',
            '/home/dread/etc/norway/norway.ini': '''
[DEFAULT]
debug = true

[app:main]
ckan.plugins = stats
''',
            })
        
        ckan_machine = CkanMachine.detect(machine=mock_machine)
        assert len(ckan_machine.ckan_instances) == 1, ckan_machine.ckan_instances
        assert_equal(ckan_machine.get_instance(None)['ckan_config_filepath'],
                     '/home/dread/etc/norway/norway.ini')

class TestWsgiScript:
    def test_basic(self):
        mock_machine = MockMachine({
            '/home/dread/etc/ckan.py': '''
from paste.deploy import loadapp
application = loadapp('config:/home/dread/etc/ckan.ini')
            '''
            })
        wsgi_script_filename = '/home/dread/etc/ckan.py'
        wsgi_script = WsgiScript(wsgi_script_filename, machine=mock_machine)
        assert 'paste.deploy' in wsgi_script.lines[1], wsgi_script.lines[1]

class TestCkanConfig:
    def test_basic(self):
        mock_machine = MockMachine({
            '/home/dread/etc/ckan.ini': '''
# ckan - Pylons configuration
[DEFAULT]
debug = true

[server:main]
use = egg:Paste#http
host = 0.0.0.0
            '''
            })
        ckan_config_filename = '/home/dread/etc/ckan.ini'
        ckan_config = CkanConfig(ckan_config_filename, machine=mock_machine)
        assert_equal(ckan_config.lines[1], '# ckan - Pylons configuration')
        assert_equal(set(ckan_config.section_dicts.keys()),
                     set(('DEFAULT', 'server:main')))
        assert_equal(ckan_config.section_dicts['server:main'],
                     {'use': 'egg:Paste#http',
                      'host': '0.0.0.0'})
        assert_equal(ckan_config.section_dicts['server:main'].start_line, 6)
        assert_equal(ckan_config.section_dicts['server:main'].finish_line, 9)
        assert_equal(ckan_config.lines[
            ckan_config.section_dicts['server:main'].start_line:
            ckan_config.section_dicts['server:main'].finish_line],
                     ['use = egg:Paste#http', 'host = 0.0.0.0', ''])


wsgi_py_without_pyenv = '''
import os
import sys
from apachemiddleware import MaintenanceResponse

symlink_filepath = __file__
if os.path.basename(symlink_filepath) == 'wsgi.py':
    print usage
    sys.exit(1)
config_filepath = symlink_filepath.replace('.py', '.ini')
assert os.path.exists(config_filepath), 'Cannot find file %r (from symlink %r)' % (config_filepath, __file__)

# enable logging
from paste.script.util.logging_config import fileConfig
fileConfig(config_filepath)

from paste.deploy import loadapp
application = loadapp('config:%s' % config_filepath)
application = MaintenanceResponse(application)
'''

wsgi_py_with_pyenv = '''
import os
instance_dir = '/var/lib/ckan/dgu'
config_dir = '/etc/ckan/dgu'
config_file = 'dgu.ini'
pyenv_bin_dir = os.path.join(instance_dir, 'pyenv', 'bin')
activate_this = os.path.join(pyenv_bin_dir, 'activate_this.py')
execfile(activate_this, dict(__file__=activate_this))
# this is werid but without importing ckanext first import of paste.deploy will fail
#import ckanext
config_filepath = os.path.join(config_dir, config_file)
if not os.path.exists(config_filepath):
    raise Exception('No such file %r'%config_filepath)
from paste.deploy import loadapp
from paste.script.util.logging_config import fileConfig
fileConfig(config_filepath)
application = loadapp('config:%s' % config_filepath)
from apachemiddleware import MaintenanceResponse
application = MaintenanceResponse(application)
'''

config_ini = '''
[handler_file]
class = handlers.RotatingFileHandler
formatter = generic
level = NOTSET
args = ('/var/log/ckan/ckan.log', 'a', 2000000, 9)
'''
