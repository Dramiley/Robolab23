#!/usr/bin/env python3

"""
A file that takes arguments and copies given files to the robot

Usage:
    deploy_files.py <files>...
"""
import json
import os
import subprocess
import sys

files = sys.argv[1:]

abs_path = os.path.dirname(os.path.abspath(__file__)) + "/"
settings_file = abs_path + 'robolab-deploy-lite/.bin/settings.json'
ssh_key = abs_path + 'robolab-deploy-lite/.bin/brick_id_rsa'
# read settings
with open(settings_file) as json_file:
    settings = json.load(json_file)

for file in files:
    # copy via scp

    abs_file = abs_path + "src/" + file

    # Connect with SSH-PubKey and synchronize files
    subprocess.run(
        ['scp',
         '-i', str(ssh_key),
         '-o', 'IdentitiesOnly=yes',
         '-o', 'StrictHostKeyChecking=no',
         str(abs_file),
         'robot@{}:/home/robot/src/{}'.format(settings['ip'], file),
         ])
