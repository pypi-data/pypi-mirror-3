""" Run an interactive console after including AppEngine and project libraries. """

import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)-8s %(asctime)s %(filename)s:%(lineno)s] %(message)s')

from google.appengine.api import yaml_errors
from google.appengine.tools import dev_appserver
from google.appengine.tools import dev_appserver_main

config = matcher = None

try:
    config, matcher, from_cache = dev_appserver.LoadAppConfig(".", {}, default_partition='dev')
except yaml_errors.EventListenerError, e:
    logging.error('Fatal error when loading application configuration:\n' +
                                    str(e))
except dev_appserver.InvalidAppConfigError, e:
    logging.error('Application configuration file invalid:\n%s', e)

args = dev_appserver_main.DEFAULT_ARGS.copy()
dev_appserver.SetupStubs(config.application, **args)

if __name__ == "__main__":
    banner = "Interactive App Engine Shell for app-id '%s'" % config.application
    try:
        import IPython
        sh = IPython.Shell.IPShellEmbed(argv='', banner=banner)
        sh(global_ns={}, local_ns={})
    except:
        try:
            from IPython import embed
            embed()
        except:
            try:
                from IPython import embed
                embed()
            except:
                import code
                console = code.InteractiveConsole()
                console.interact(banner)
