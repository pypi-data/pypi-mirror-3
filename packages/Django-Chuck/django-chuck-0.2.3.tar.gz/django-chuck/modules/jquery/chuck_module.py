import subprocess
import os

description = """
Installs the latest jQuery version into the static folders at:
<STATIC_URL>/scripts/libs/jquery/jquery.js
<STATIC_URL>/scripts/libs/jquery/jquery.min.js

For more information, visit:
http://jquery.org/
"""

def post_build():

    jquery_dir = os.path.join(project_dir, 'static/scripts/libs/jquery')
    if not os.path.exists(jquery_dir):
        os.makedirs(jquery_dir)
    commands = [
        'cd '+jquery_dir,
        'touch jquery.js',
        'touch jquery.min.js',
        'curl http://code.jquery.com/jquery-latest.js > jquery.js',
        'curl http://code.jquery.com/jquery-latest.min.js > jquery.min.js',
        ]
    kwargs = dict(
        shell=True
    )
    process = subprocess.Popen('; '.join(commands), **kwargs)
    stdout, stderr = process.communicate()