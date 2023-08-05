import ConfigParser
import StringIO
from fabric.decorators import task
from fabric.api import env, get, put
import os
from fabric.contrib.files import exists
from .utils import config
import posixpath
from .utils import STATIC_COLLECTED, DATA_DIRECTORY
from pprint import pformat
from fabric.operations import run

def django_exec(dictionary = {}, tool="buildout"):
    config = ConfigParser.RawConfigParser()
    config_file = os.path.join(env.path, "config.ini")
    django_base = "." # default to current dir
    if exists(config_file):
        output = StringIO.StringIO()
        get(u"%s" % config_file, output)
        output.seek(0)
        config.readfp(output)
    
        try:
            tool = config.get("checkout", "tool")
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            tool = "buildout" # default to buildout

        try:
            django_base = config.get("django", "base")
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            pass
    if django_base == ".":
        django_base = ""
    if tool == "buildout":
        cmd = os.path.join(env.path, django_base, "bin/django")
        django_settings = os.path.join(env.path, django_base, "settings.py")
    else:
        cmd = "%s %s" % (os.path.join(env.path, "bin/python"), os.path.join(env.path, django_base, "manage.py"))
        django_settings = os.path.join(env.path, django_base, "settings.py")
    dictionary['django_exec'] = cmd
    dictionary['django_settings'] = django_settings
    dictionary['checkout_tool'] = tool
    return dictionary
    
def django_settings_file(dictionary = {}): # TODO: Make docs for this!
    return django_exec().get("django_settings")

@task
def manage(*args):
    """
    Proxy for manage.py
    """
    config.django_manage(" ".join(args))
    
@task
def collectstatic(staticdir='static'): # As defined in puppet config
    run(('cd %(path)s; mkdir -p ' + staticdir) % env)
    manage("collectstatic", "--noinput", "--link")
    
@task
def append_settings():
    # TODO: make it work with multisites!
    append = config.sites["main"].get("django").get("append_settings", False)
    if append:
        site_config = config.sites["main"]
        settings_file_path = django_settings_file()
        print "Appending auto generated settings to", settings_file_path
        output = StringIO.StringIO()
        get(u"%s" % os.path.join(env.path, "../config/django.py"), output)
        output.seek(0)
        manual_settings = output.read()

        # DATABASES
        additional_settings = "DATABASES = %s\n" % pformat(config.sites["main"].get("deployment").get("databases"))

        # CACHES
        processes = config.sites["main"].get("processes")
        cache_dict = {
            'default': {
                'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
                'LOCATION': 'unix:%s' % [processes[x] for x in processes if processes[x]["type"] == "memcached"][0].get("socket"),
            }
        }
        additional_settings += "CACHES = %s\n" % pformat(cache_dict)

        # PATHS
        additional_settings += """
STATIC_ROOT = "%(static_root)s"
MEDIA_ROOT = "%(media_root)s"
""" % {
            'static_root': posixpath.join(site_config.get("deployment").get("path"), STATIC_COLLECTED),
            'media_root': posixpath.join(site_config.get("deployment").get("path"), DATA_DIRECTORY),
        }

        output = StringIO.StringIO()
        get(settings_file_path, output)
        output.seek(0)
        settings_file = output.read()


        run("mkdir -p %s" % posixpath.join(site_config.get("deployment").get("path"), "_gen/"))
        put(StringIO.StringIO("%s\n%s\n%s" % (settings_file, additional_settings, manual_settings)), site_config.get("deployment").get("generated_settings_path"))
        put(StringIO.StringIO(""), posixpath.join(site_config.get("deployment").get("path"), "_gen/__init__.py"))