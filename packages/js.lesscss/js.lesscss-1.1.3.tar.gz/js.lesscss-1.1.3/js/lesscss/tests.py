# -*- coding: utf-8 -*-
import os
import sys
from js.lesscss import library, LessResource
from fanstatic.core import NeededResources

stderr = sys.stderr

def test_resource():

    resource = LessResource(library, 'my.less')

    if 'LESSC' not in os.environ:
        stderr.write(('WARN: Please export a LESSC variable. '
                      'Test skipped...'))
        return

    nr = NeededResources(resources=[resource], debug=True)
    assert len(nr.resources()) > 1, nr.resources()
    tag = nr.render()
    assert 'less.min.js"' in tag, tag
    assert 'type="text/x-less" href="/fanstatic/less/my.less"' in tag, tag

    nr = NeededResources(resources=[resource], minified=True)
    tag = nr.render()
    assert 'less.min.js"' in tag, tag
    assert 'type="text/css" href="/fanstatic/less/my.less.min.css"' in tag, tag

    nr = NeededResources(resources=[resource])
    tag = nr.render()
    assert 'less.min.js"' in tag, tag
    assert 'type="text/css" href="/fanstatic/less/my.less.min.css"' in tag, tag

