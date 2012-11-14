"""
unittests for random mover

designed to be run with py.test
"""
import datetime

import numpy as np

import gnome
from gnome import movers
from gnome import basic_types, spill
from gnome.utilities import time_utils 
from gnome.utilities import projections


import pytest


def test_exceptions():
    """
    Test ValueError exception thrown if improper input arguments
    """
    with pytest.raises(ValueError):
        movers.RandomMover(diffusion_coef=0)


class TestRandomMover():
    """
    gnome.RandomMover() test

    """
    num_le = 5
    start_pos = np.zeros((num_le,3), dtype=basic_types.world_point_type)
    rel_time = datetime.datetime(2012, 8, 20, 13)    # yyyy/month/day/hr/min/sec
    model_time = time_utils.sec_to_date(time_utils.date_to_sec(rel_time) + 1)
    time_step = 15*60 # seconds

    pSpill = spill.PointReleaseSpill(num_le, start_pos, rel_time, persist=-1)

    mover = movers.RandomMover()
    
    def reset_pos(self):
        self.pSpill['positions'] = (0.,0.,0.)
        print self.pSpill['positions']
    
    def test_string_representation_matches_repr_method(self):
        assert repr(self.mover) == 'Random Mover'
        assert str(self.mover) == 'Random Mover'

    def test_id_matches_builtin_id(self):
        assert id(self.mover) == self.mover.id
       
    def test_change_diffusion_coef(self):
        self.mover.diffusion_coef = 200000
        print self.mover.diffusion_coef
        assert self.mover.diffusion_coef == 200000 
        
    def test_prepare_for_model_step(self):
        """
        Simply tests the method executes without exceptions
        """
        self.mover.prepare_for_model_step(self.model_time, self.time_step)
        assert True

start_locs = [(0.0,0.0,0.0),
              (30.0, 30.0, 30.0),
              (-45.0, -60.0, 30.0),
              ]

timesteps = [36, 360, 3600]

test_cases = [(loc, step) for loc in start_locs for step in timesteps]

@pytest.mark.parametrize( ("start_loc","time_step"), test_cases)
def test_variance1(start_loc, time_step):
    """
    After a few timesteps the variance of the particle positions should be
    similar to the computed value: var = Dt
    """
    num_le = 1000
    start_time = datetime.datetime(2012,11,10,0)
    spill = gnome.spill.PointReleaseSpill(num_le, start_loc, start_time)
    D = 100000
    num_steps = 10
    spill.reset()

    rand = movers.RandomMover(diffusion_coef=D)

    model_time = start_time
    for i in range(num_steps):
        model_time += datetime.timedelta(seconds=time_step)
        spill.prepare_for_model_step(model_time, time_step)
        rand.prepare_for_model_step(model_time, time_step)
        delta = rand.get_move(spill, time_step, model_time)
        #print "delta:", delta
        spill['positions'] += delta
        #print spill['positions']
    # compute the variances:
    # convert to meters
    pos = projections.FlatEarthProjection.lonlat_to_meters(spill['positions'], start_loc)
    var = np.var(pos, axis=0)

    expected = 2.0 * (D * 1e-4) * num_steps * time_step # D converted to meters^s/s

    assert np.allclose(var, (expected, expected, 0.0), rtol= 0.1 )

       
if __name__=="__main__":
    tw = TestRandomMover()
    tw.test_prepare_for_model_step()
    tw.test_change_diffusion_coef()