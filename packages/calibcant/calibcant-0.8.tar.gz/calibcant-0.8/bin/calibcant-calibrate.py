#!/usr/bin/env python
# calibcant - tools for thermally calibrating AFM cantilevers
#
# Copyright

"""Run a cantilever calibration using the default AFM
(``pyafm.storage.load_afm()``).
"""

import os
import time as _time

from calibcant.calibrate import Calibrator as _Calibrator
from pyafm.storage import load_afm as _load_afm
import calibcant.config as _config


def main(args):
    timestamp = '{0}-{1:02d}-{2:02d}T{3:02d}-{4:02d}-{5:02d}'.format(
        *_time.localtime())
    filename = '{}-calibcant-data.h5'.format(timestamp)
    config = _config.CalibrateConfig()
    config['bump'] = _config.BumpConfig()
    config['bump'].update(
        {'model':_config.Linear, 'initial-position':-150e-9})
    config['temperature'] = _config.TemperatureConfig()
    config['vibration'] = _config.VibrationConfig()
    devices = []
    try:
        afm = _load_afm()
        afm.load_from_config(devices=devices)
        calibrator = _Calibrator(config=config, afm=afm)
        calibrator.setup_config()
        deflection = afm.piezo.read_deflection()
        afm.stepper_approach(target_deflection=deflection + 1e3)
        k,k_s,data = calibrator.calibrate(filename=filename)
    finally:
        for device in devices:
            device.close()
    print 'k: {:g} +/- {:g}'.format(k, k_s)
    return 0

if __name__ == '__main__':
    import sys

    sys.exit(main(sys.argv[1:]))
