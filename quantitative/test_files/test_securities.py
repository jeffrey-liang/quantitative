#!/usr/bin/env python
# -*- coding: utf-8 -*-

from securities import Security
import pandas as pd
import numpy as np

times = ['2017-11-10 09:30:00.000000000',  '2017-11-10 09:46:32.278115304',
         '2017-11-10 09:46:32.278133425', '2017-11-10 09:46:32.278142489',
         '2017-11-10 09:46:32.278175650', '2017-11-10 09:46:32.278182576',
         '2017-11-10 09:46:32.278187841', '2017-11-10 09:46:32.278192693',
         '2017-11-10 16:00:00.000000000', '2017-12-10 09:30:00.000000000',
         '2017-12-10 09:46:32.278221346', '2017-12-10 09:46:32.278229858',
         '2017-12-10 09:46:32.278235405']

times = [pd.Timestamp(time) for time in times]

s = Security('S')
s.time = times[1]
s._initalize_history(times)
#s._history.loc['bid', times[0]] = 100
s._history.loc['bid', pd.Timestamp('2017-12-10 09:46:32.558235405')] = 100
print(s._history)

#print(s.history('bid', 10))

