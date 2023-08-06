# Copyright (C) 2012 Linaro Limited
#
# Author: Zygmunt Krynicki <zygmunt.krynicki@linaro.org>
#
# This file is part of LAVA Fast Models
#
# LAVA Fast Models is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License version 3
# as published by the Free Software Foundation
#
# LAVA Fast Models is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with LAVA Fast Models.  If not, see <http://www.gnu.org/licenses/>.

import subprocess


class LowLevelSimulator(object):
    """
    Direct access to the model_shell/model_shell64

    There is very little additional code or features. You can set options prior
    to starting the simulator. The actual simulator binary is wrapped by the
    model you have to pass. This class only controls the options and the
    execution.
    """

    def __init__(self, model, axf, options):
        self.model = model
        self.axf = axf
        self.options = options
        self.proc = None

    def start(self):
        self.proc = subprocess.Popen()

    def end(self):
        self.proc.kill()

    @property
    def serial_console(self):
        raise NotImplementedError()
