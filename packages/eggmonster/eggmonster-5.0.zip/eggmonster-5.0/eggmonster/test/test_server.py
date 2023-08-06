import sys
import os

import dingus

from eggmonster import server

def fake_stat(filepath):
    # create a fake time that's always the same for a given path
    fake_time = hash(filepath) % 2**32
    return os.stat_result((0,)*7 + (fake_time,)*3)

class TestConfig(object):
    if sys.version_info < (2,6):
        sample_listing = ['%(num)s.yaml' % vars() for num in xrange(1,11)]
    else:
        sample_listing = ['{num}.yaml'.format(**vars()) for num in xrange(1,11)]
    listdir_patch = dingus.patch(
        'os.listdir',
        dingus.Dingus(return_value=sample_listing),
    )
    stat_patch = dingus.patch(
        'os.stat',
        fake_stat,
    )
    pathjoin_patch = dingus.patch(
        'os.path.join',
        lambda *args: args[-1],
    )

    @pathjoin_patch
    @stat_patch
    @listdir_patch
    def test_config_nums(self):
        assert sorted(server.config_nums()) == range(1,11)

    @pathjoin_patch
    @stat_patch
    @listdir_patch
    def test_latest_config(self):
        assert server.latest_config() == 10
