
#
# jsSip-demo -- Demonstrate using jsSip WebRTC via Asterisk PBX, Twilio
#
# Copyright (c) 2024, Dominion R&D Corp.
#
# jsSip-demo is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.  See the LICENSE file at the top of the source tree.
#
# jsSip-demo is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#

from __future__ import absolute_import, print_function, division

__author__                      = "Perry Kundert"
__email__                       = "perry@dominionrnd.com"
__copyright__                   = "Copyright (c) 2024 Dominion Research & Development Corp."
__license__                     = "Dual License: GPLv3 (or later) and Commercial (see LICENSE)"

__name__			= "jsSip_demo"

__all__                         = []

# These modules form the public interface of routeros_ssh; always load them into the main namespace
from .version		import __version__, __version_info__
