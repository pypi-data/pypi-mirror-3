import os
import re
from django_chuck.commands.base import BaseCommand

class Command(BaseCommand):
    help = "Search available modules matching given name or description"

    def __init__(self):
        super(Command, self).__init__()

        # Disable default checks because this command isn't project-related
        self.no_default_checks = True

        self.opts = [("pattern", {
            "help": "search pattern",
            "default": "",
        })]


    def handle(self, args, cfg):
        super(Command, self).handle(args, cfg)

        self.print_header("MATCHING MODULES")

        for (module_name, module) in self.get_module_cache().items():
            if re.search(self.args.pattern, module_name) or \
               re.search(self.args.pattern, module.get_description()):
                print "-------------------------------------------------------------------------------"
                print "[%s]" % (module_name,)
                print "-------------------------------------------------------------------------------"

                if module.get_description():
                    print module.get_description() + "\n"
                else:
                    print "\nNo description available\n\n"