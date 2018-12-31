#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import uuid
import time 


uuid_list = []
numpy_list = []

t0 = time.time()

for x in range(10000):
    uuid_list.append(uuid.uuid4())
print(time.time() - t0)

for x in range(10000):
    numpy_list.append(np.random.randn(1))
print(time.time() - t0)

