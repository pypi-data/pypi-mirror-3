=============
Kepub Toolbox
=============

Kepub Toolbox provides several utilities for conversion of ebook format

Typical usage for transforming an Open Office Document (.odt) into a DocBook
would look like this::

    #!/usr/bin/env python

	import sys
	from kepub.wpo.odt import Odt

	o = Odt(sys.argv[1])
	o.to_docbook()


Download
========

Overall project is published under Gnu Common License version 3 and can be 
freely downloaded from PyPI or forked on `BitBucket <https://bitbucket.org/steppo40/kepub-toolbox/>`_.
