# This file is part of beets.
# Copyright 2011, Adrian Sampson.
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
# 
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

"""An example plugin.
"""

import random
from beets.plugins import BeetsPlugin

class ExamplePlugin(BeetsPlugin):
    pass

@ExamplePlugin.template_func('rand')
def rand(text):
    return random.choice(text)

@ExamplePlugin.template_field('alpha')
def alpha(item):
    return item.title < 'M'
