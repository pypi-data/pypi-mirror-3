
from neo import SpikeTrain, Segment, Block
from neo.io.hdf5io import NeoHdf5IO
import numpy as np


block = Block(name="test_data")
block.annotate(foo="bar")

segment = Segment(name="trial01")
segment.annotate(stimulus="grating")

block.segments.append(segment)

spikes = [SpikeTrain(np.arange(i, 10+i), t_start=0.0, t_stop=20.0, units="ms")
          for i in range(7)]

segment.spiketrains.extend(spikes)


file = NeoHdf5IO(filename="test876.h5")

file.save(block)

file.close()
