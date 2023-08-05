from setuptools import setup, find_packages

setup(
    name = 'plexshell',
    version = '0.0.2',
    description = 'A shell to interact with the Plex Media Server',
    author = 'Jamie Kirkpatrick',
    author_email = 'jamie@plexinc.com',
    packages = find_packages(exclude = ["tests", "doc"]),
    url = 'https://github.com/jkp/plexshell',
    download_url = 'https://github.com/jkp/plexshell/downloads',
    install_requires = [
        'lxml'
    ],
    entry_points = {
        'console_scripts': [
            'psh = plexshell.scripts.shell:main',
        ],
    },
    zip_safe = True
)
