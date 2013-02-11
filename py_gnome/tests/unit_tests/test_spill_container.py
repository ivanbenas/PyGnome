"""
Tests the SpillContainer class
"""

from datetime import datetime, timedelta

import pytest
import numpy as np

from gnome import basic_types
from gnome.spill_container import SpillContainer, TestSpillContainer
from gnome.spill import Spill, SurfaceReleaseSpill, SubsurfaceReleaseSpill

def test_simple_init():
    sc = SpillContainer()
    assert sc

def test_test_spill_container():
    pos = (28.0, -75.0, 0.0)
    num_elements = 10
    sc = TestSpillContainer(num_elements, (28, -75, 0) )

    assert sc['positions'].shape == (10, 3)

    assert np.array_equal( sc['positions'][0], pos )
    assert np.array_equal( sc['positions'][-1], pos )


## real tesing involves adding spills!
def test_one_simple_spill():
    start_time = datetime(2012, 1, 1, 12)
    start_position = (23.0, -78.5, 0.0)
    num_elements =  100
    sc = SpillContainer()
    spill = SurfaceReleaseSpill(num_elements,
                                start_position,
                                start_time)
    sc.spills.add(spill)
    sc.release_elements(start_time)

    assert sc.num_elements == num_elements

    assert sc['positions'].shape == (num_elements, 3)
    assert sc['last_water_positions'].shape == (num_elements, 3)

    sc.prepare_for_model_step(start_time + timedelta(hours=24) )

    assert sc['positions'].shape == (num_elements, 3)
    assert sc['last_water_positions'].shape == (num_elements, 3)

    assert np.array_equal( sc['positions'][0], start_position )

## multiple spills with different release times:
def test_multiple_spills():
    start_time = datetime(2012, 1, 1, 12)
    start_time2 = datetime(2012, 1, 2, 12)
    start_position = (23.0, -78.5, 0.0)
    num_elements =  100
    sc = SpillContainer()
    spill = SurfaceReleaseSpill(num_elements,
                                start_position,
                                start_time)

    sp2 = SurfaceReleaseSpill(num_elements,
                                start_position,
                                start_time2)

    sc.spills += [spill, sp2]
    print sc.spills

    sc.release_elements(start_time)

    assert sc['positions'].shape == (num_elements, 3)
    assert sc['last_water_positions'].shape == (num_elements, 3)

    sc.release_elements(start_time + timedelta(hours=24) )

    assert sc['positions'].shape == (num_elements*2, 3)
    assert sc['last_water_positions'].shape == (num_elements*2, 3)

    ## check the get_spill method
    assert sc.spills[spill.id] == spill
    assert sc.spills[sp2.id] == sp2

    ## check remove
    sc.spills.remove(spill.id)
    with pytest.raises(KeyError):
        assert sc.spills[spill.id] is None # it shouldn't be there anymore.


def test_rewind():
    start_time = datetime(2012, 1, 1, 12)
    start_time2 = datetime(2012, 1, 2, 12)
    start_position = (23.0, -78.5, 0.0)
    num_elements =  100
    sc = SpillContainer()
    spill = SurfaceReleaseSpill(num_elements,
                                start_position,
                                start_time)

    sp2 = SurfaceReleaseSpill(num_elements,
                                start_position,
                                start_time2)

    sc.spills.add(spill)
    sc.spills.add(sp2)
    sc.prepare_for_model_step(start_time)
    sc.prepare_for_model_step(start_time + timedelta(hours=24) )

    sc.rewind()
    assert spill.num_released == 0
    assert sp2.num_released == 0

def test_rewind2():
    """
    test that extra arrays are removed on a rewind

    # not much of a test, really -- add more?
    """
    start_time = datetime(2012, 1, 1, 12)
    start_time2 = datetime(2012, 1, 2, 12)
    start_position = (23.0, -78.5, 0.0)
    num_elements =  100
    sc = SpillContainer()
    spill = Spill(num_elements)

    sp2 = SurfaceReleaseSpill(num_elements,
                                start_position,
                                start_time2)

    sc.spills.add(spill)
    sc.spills.add(sp2)

    sc.prepare_for_model_step(start_time)
    sc.prepare_for_model_step(start_time + timedelta(hours=24) )

    sc.spills.remove(spill.id)

    sc.rewind()
    print "id of spill 2", sp2.id
    assert sp2.num_released == 0


def test_data_access():
    sp = TestSpillContainer(10, (0,0,0),)

    sp['positions'] += (3.0, 3.0, 3.0)

    assert np.array_equal(sp['positions'],
                          np.ones( (10, 3), dtype=basic_types.world_point_type ) * 3.0
                          )


def test_data_setting():
    sp = TestSpillContainer(num_elements = 10 )

    new_pos = np.ones( (10, 3), dtype=basic_types.world_point_type ) * 3.0

    sp['positions'] = new_pos

    assert np.array_equal(sp['positions'],
                          new_pos
                          )


def test_data_setting_error1():
    """
    Should get an error when trying to set the data to a different size array
    """
    sp = TestSpillContainer(num_elements =  10)

    new_pos = np.ones( (12, 3), dtype=basic_types.world_point_type ) * 3.0
    with pytest.raises(ValueError):
        sp['positions'] = new_pos


def test_data_setting_error2():
    """
    Should get an error when trying to set the data to a different type array
    """
    sp = TestSpillContainer(num_elements =  10)

    new_pos = np.ones( (10, 3), dtype=np.int32 )

    with pytest.raises(ValueError):
        sp['positions'] = new_pos


def test_data_setting_error3():
    """
    Should get an error when trying to set the data to a different shape array
    """
    sp = TestSpillContainer(num_elements =  10)

    new_pos = np.ones( (10, 4), dtype=basic_types.world_point_type ) * 3.0

    with pytest.raises(ValueError):
        sp['positions'] = new_pos


def test_data_setting_new():
    """
    Should be able to add a new data array
    """
    sp = TestSpillContainer(num_elements =  10)

    new_arr = np.ones( (10, 3), dtype=np.float64 )

    sp['new_name'] = new_arr

    assert sp['new_name'] is new_arr


def test_data_setting_new_list():
    """
    Should be able to add a new data that's not a numpy array
    """
    sp = TestSpillContainer(num_elements =  10)

    new_arr = range(10)

    sp['new_name'] = new_arr

    assert np.array_equal(sp['new_name'],  new_arr)


def test_data_arrays():
    """
    SpillContainer manages a number of numpy arrays that represent the properties
    of the LEs that have been released by the contained spills.
    Here we test that the data arrays are behaving as expected.
    """
    start_time1 = datetime(2012, 1, 1, 12)
    start_time2 = datetime(2012, 1, 2, 12)
    start_time3 = datetime(2012, 1, 3, 12)
    start_time4 = datetime(2012, 1, 4, 12)
    start_time5 = datetime(2012, 1, 5, 12)
    start_position = (23.0, -78.5, 0.0)
    num_elements =  5
    sc = SpillContainer()
    sp1 = SurfaceReleaseSpill(num_elements,
                              start_position,
                              start_time1)

    sp2 = SurfaceReleaseSpill(num_elements,
                              start_position,
                              start_time2)

    sp3 = SurfaceReleaseSpill(num_elements,
                              start_position,
                              start_time3)

    sp4 = SubsurfaceReleaseSpill(num_elements,
                                 start_position,
                                 start_time4)

    sp5 = SurfaceReleaseSpill(num_elements,
                              start_position,
                              start_time5)

    sc.spills += [sp1, sp2, sp3]

    print sc.spills

    # as we move forward in time, the spills will release LEs
    # in an expected way
    sc.release_elements(start_time1)

    assert sc['positions'].shape == (num_elements, 3)
    assert sc['last_water_positions'].shape == (num_elements, 3)
    assert sc['windages'].shape == (num_elements, )  # it should be there.
    with pytest.raises(KeyError):
        assert sc['water_currents'].shape == (num_elements, 3)  # it shouldn't be there.

    sc.release_elements(start_time1 + timedelta(hours=24))

    assert sc['positions'].shape == (num_elements*2, 3)
    assert sc['last_water_positions'].shape == (num_elements*2, 3)
    assert sc['windages'].shape == (num_elements*2, )  # it should be there.
    with pytest.raises(KeyError):
        assert sc['water_currents'].shape == (num_elements*2, 3)  # it shouldn't be there.

    sc.release_elements(start_time2 + timedelta(hours=24))

    assert sc['positions'].shape == (num_elements*3, 3)
    assert sc['last_water_positions'].shape == (num_elements*3, 3)
    assert sc['windages'].shape == (num_elements*3, )  # it should be there.
    with pytest.raises(KeyError):
        assert sc['water_currents'].shape == (num_elements*3, 3)  # it shouldn't be there.


    # - When we delete a spill, the previously released LEs from that spill
    #   will stay in the data arrays
    #   - All LEs, including from the deleted spill, will maintain their spill_num property.
    # - When a spill is added with new properties, new items representing those properties
    #   will be created in the data arrays and back-filled to accommodate the
    #   previously released LEs
    del sc.spills[sp2.id]
    sc.spills += sp4
    sc.release_elements(start_time3 + timedelta(hours=24))

    assert sc['positions'].shape == (num_elements*4, 3)
    assert sc['last_water_positions'].shape == (num_elements*4, 3)
    assert sc['windages'].shape == (num_elements*4, )
    assert sc['water_currents'].shape == (num_elements*4, 3)  # new property should be there with the right shape.
    assert set(sc['spill_num']) == set([0,1,2,3])  # All spill_nums, even the ones that were deleted

    # - When we delete a spill, any properties that are not needed by the still
    #   existing spills will be purged.  This purging will happen on the next
    #   release after the delete.
    del sc.spills[sp4.id]
    sc.spills += sp5
    sc.release_elements(start_time4 + timedelta(hours=24))

    assert sc['positions'].shape == (num_elements*5, 3)
    assert sc['last_water_positions'].shape == (num_elements*5, 3)
    assert sc['windages'].shape == (num_elements*5, )
    with pytest.raises(KeyError):
        assert sc['water_currents'].shape == (num_elements*5, 3)  # extra property from deleted spill should go away
    assert set(sc['spill_num']) == set([0,1,2,3,4])  # All spill_nums, even the ones that were deleted


def test_uncertain_copy():
    """
    test whether creating an uncertain copy of a spill_container works
    """
    start_time = datetime(2012, 1, 1, 12)
    start_time2 = datetime(2012, 1, 2, 12)

    start_position =  (23.0, -78.5, 0.0)
    start_position2 = (45.0,  75.0, 0.0)

    num_elements =  100

    sc = SpillContainer()
    spill = SurfaceReleaseSpill(num_elements,
                                start_position,
                                start_time)

    sp2 = SurfaceReleaseSpill(num_elements,
                                start_position2,
                                start_time2)

    sc.spills.add(spill)
    sc.spills.add(sp2)

    u_sc = sc.uncertain_copy()

    assert u_sc.is_uncertain
    assert len(sc.spills) == len(u_sc.spills)

    # make sure they aren't references to the same spills
    assert sc.spills[spill.id] not in u_sc.spills
    assert sc.spills[sp2.id] not in u_sc.spills

    # make sure they have unique ids:
    for id1 in [s.id for s in sc.spills]:
        for id2 in [s.id for s in u_sc.spills]:
            print id1, id2
            assert not id1==id2

    # do the spills work?

    sc.release_elements(start_time)

    assert sc['positions'].shape == (num_elements, 3)
    assert sc['last_water_positions'].shape == (num_elements, 3)

    # nothing released yet.
    assert u_sc['positions'].shape[0] == 0

    # now release second set:
    u_sc.release_elements(start_time)
    # elements should be there.
    assert u_sc['positions'].shape == (num_elements, 3)
    assert u_sc['last_water_positions'].shape == (num_elements, 3)

    # next release:
    sc.release_elements(start_time + timedelta(hours=24) )

    assert sc['positions'].shape == (num_elements*2, 3)
    assert sc['last_water_positions'].shape == (num_elements*2, 3)

    # second set should not have changed
    assert u_sc['positions'].shape == (num_elements, 3)
    assert u_sc['last_water_positions'].shape == (num_elements, 3)

    # release second set
    u_sc.release_elements(start_time + timedelta(hours=24) )
    assert u_sc['positions'].shape == (num_elements*2, 3)
    assert u_sc['last_water_positions'].shape == (num_elements*2, 3)


def test_ordered_collection_api():
    start_time = datetime(2012, 1, 1, 12)
    start_position = (23.0, -78.5, 0.0)
    num_elements =  100

    sc = SpillContainer()
    sc.spills += SurfaceReleaseSpill(num_elements,
                                     start_position,
                                     start_time)
    assert len(sc.spills) == 1


if __name__ == "__main__":
    test_rewind2()

