import sys


def main(settings_file):
    try:
        mod = __import__(settings_file)
        components = settings_file.split('.')
        for comp in components[1:]:
            mod = getattr(mod, comp)

    except ImportError:
        # XXX: Hack for python < 2.6
        _, e, _ = sys.exc_info()
        sys.stderr.write("Error loading the settings module '%s': %s"
                            % (settings_file, e))
        sys.exit(1)

    from django.core import management
    management.execute_manager(mod)
