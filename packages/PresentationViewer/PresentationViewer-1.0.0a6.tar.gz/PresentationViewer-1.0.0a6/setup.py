#! /usr/bin/env python
"""Set up the presentationviewer script"""
from setuptools import setup
import os
version = [
    (line.split('=')[1]).strip().strip('"').strip("'")
    for line in open(os.path.join('presentationviewer','__init__.py'))
    if line.startswith( '__version__' )
][0]

if __name__ == "__main__":
    setup(
        name = 'PresentationViewer',
        version = version,
        author = 'VRPlumber Consulting Inc.',
        author_email = 'mcfletch@vrplumber.com',
        packages = ['presentationviewer'],
        package_dir = {
            'presentationviewer': 'presentationviewer',
        },
        license = 'MIT',
        options = {
            'sdist': {
                'force_manifest': True,
                'formats': ['gztar','zip'],
            },
        },
        zip_safe = False,
        entry_points = dict(
            console_scripts = [
                'presentation-viewer = presentationviewer.viewer:main',
            ],
        ),
    )
    
