import sys

py26 = sys.version_info >= (2,6)
py27 = sys.version_info >= (2,7)
json_requirement = ['simplejson'] if not py26 else []
argparse_requirement = ['argparse'] if not py27 else []

setup_params = dict(
    name='eggmonster',
    use_hg_version=dict(increment='0.1'),
    author="Jamie Turner/YouGov",
    author_email="support@yougov.com",
    url="https://bitbucket.org/yougov/eggmonster",
    packages=["eggmonster", "eggmonster.client", "eggmonster.control",
        "eggmonster.commands",],
    install_requires=[
        "PyYAML >= 3.0.9",
        "httplib2",
        "zc.lockfile==1.0",
        "jaraco.compat",
        ] + json_requirement + argparse_requirement,
    extras_require=dict(
        server = [
            'eventful',
            'event',
            ],
        ),
    entry_points = {
        'console_scripts' : [
            'emget = eggmonster.emget:run',
            'emup = eggmonster.emup:run',
            "em = eggmonster.commands.em:run",
            "emi = eggmonster.commands.emi:run",
            "monster_debug = eggmonster.commands.monster_debug:run",
            "monster_eggserver = eggmonster.commands.monster_eggserver:run",
            "monster_launchd = eggmonster.commands.monster_launchd:run",
            "monster_logd = eggmonster.commands.monster_logd:run",
            "monster_run = eggmonster.commands.monster_run:run",
            "monster_server = eggmonster.commands.monster_server:run",
            ]
        },
    setup_requires = [
        'hgtools',
        ],
    use_2to3 = True,
    )

if __name__ == '__main__':
    from setuptools import setup
    setup(**setup_params)
