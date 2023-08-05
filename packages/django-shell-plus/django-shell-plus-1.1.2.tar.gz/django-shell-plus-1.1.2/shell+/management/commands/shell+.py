import os
from django.core.management.base import NoArgsCommand
from optparse import make_option
import datetime

class Command(NoArgsCommand):
    help = "Runs a Python interactive interpreter."

    requires_model_validation = False

    def handle_noargs(self, **options):
        # XXX: (Temporary) workaround for ticket #1796: force early loading of all
        # models from installed apps.
        from django.db.models.loading import get_models
        loaded_models = get_models()

        import code
        # Set up a dictionary to serve as the environment for the shell, so
        # that tab completion works on objects that are imported at runtime.
        # See ticket 5082.
        imported_objects = {'datetime':datetime}
        
        # Put all of the models into the local namespace.
        for model in loaded_models:
            imported_objects[model.__name__] = model
        
        try: # Try activating rlcompleter, because it's handy.
            import readline
        except ImportError:
            pass
        else:
            # We don't have to wrap the following import in a 'try', because
            # we already know 'readline' was imported successfully.
            import rlcompleter
            readline.set_completer(rlcompleter.Completer(imported_objects).complete)
            readline.parse_and_bind("tab:complete")

        # We want to honor both $PYTHONSTARTUP and .pythonrc.py, so follow system
        # conventions and get $PYTHONSTARTUP first then import user.
        pythonrc = os.environ.get("PYTHONSTARTUP") 
        if pythonrc and os.path.isfile(pythonrc): 
            try: 
                execfile(pythonrc) 
            except NameError: 
                pass
        # This will import .pythonrc.py as a side-effect
        import user
        code.interact(local=imported_objects)