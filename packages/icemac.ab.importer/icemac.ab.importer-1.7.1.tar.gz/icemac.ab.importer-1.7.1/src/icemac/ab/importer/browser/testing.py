# Copyright (c) 2008-2011 Michael Howitz
# See also LICENSE.txt
# $Id: testing.py 1373 2011-11-03 20:01:08Z icemac $

import icemac.ab.importer.browser
import icemac.addressbook.testing


class _ImporterLayer(icemac.addressbook.testing._ZCMLAndZODBLayer):
    """Layer to test the importer."""

    package = icemac.ab.importer.browser
    defaultBases = (icemac.addressbook.testing.WSGI_TEST_BROWSER_LAYER,)


ImporterLayer = _ImporterLayer(name='ImporterLayer')
