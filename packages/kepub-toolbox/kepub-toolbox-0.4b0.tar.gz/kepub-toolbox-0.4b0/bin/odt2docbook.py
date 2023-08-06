#!/usr/bin/env python
"""Script di trasformazione da file Odt a Docbook

Utilizzo:
    odt2docbook <file odt> [<directory di output>]

"""

import sys
from kepub.wpo.odt import Odt

import logging
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

o = Odt(sys.argv[1])
if len(sys.argv) > 2:
    o.to_docbook(' '.join(sys.argv[2:]))
else:
    o.to_docbook()
