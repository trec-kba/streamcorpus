
import os
import subprocess

def test_dump():
    path = os.path.join(os.path.dirname(__file__), '../../../test-data/john-smith-tagged-by-lingpipe-0-v0_3_0.sc')
    cmd = 'python -m streamcorpus.dump %s --field stream_id --len body.clean_visible --len body.raw' % path
    print cmd
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    output = p.stdout.read()
    assert 'stream_id' in output
    assert len(output.splitlines()) == 197

    
