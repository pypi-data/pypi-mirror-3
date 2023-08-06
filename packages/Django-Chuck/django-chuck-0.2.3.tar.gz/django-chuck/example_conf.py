# Where to put virtualenvs?
virtualenv_basedir="~/work/virtualenvs"

# Where to put project dirs?
project_basedir="~/work/projects"

# Comma seperated list of dirs where Chuck should look for modules.
# . will be replaced with the Django Chuck modules dir
module_basedirs = ["."]

# comma seperated list of modules that always should be installed
default_modules=["core", "south"]

# comma seperated list of app that should additionally get installed
#default_additional_apps = ["south"]

# use virtualenvwrapper?
use_virtualenvwrapper = False

# default django settings module to use
# project_name will be automatically prepended
django_settings = "settings.dev"

# requirements file to install in virtualenv
# default: requirements_local.txt
requirements_file = "requirements_local.txt"

# version control system
# possible values: git, svn, cvs, hg
# default: git
version_control_system = "git"

# the branch you want to checkout / clone
# default is ""
branch = ""

# Python version to use by default
# If not set version of local python interpreter will be used
# python_version = "2.7"

# Where to find virtualenvs on your server?
server_virtualenv_basedir = "/home/www-data/virtualenvs"

# Where to projects on your server?
server_project_basedir = "/home/www-data/sites"

# What is your email domain?
email_domain = "localhost"

# module aliases are a list of modules under a single name
module_aliases = {
    "test": ["unittest", "jenkins"]
}

# Run in debug mode
debug = False

# Dont delete project after failure?
# delete_project_on_failure=False

# Module to use as template engine
# Default: django_chuck.template.notch_interactive.engine
template_engine = "django_chuck.template.notch_interactive.engine"
