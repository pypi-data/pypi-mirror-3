from nose.tools import *
from nose import run
from lazyrange import Range

def test_stop():
    assert_equal(list(Range(10)), range(10))
    
def test_start_stop():
    assert_equal(list(Range(5, 10)), range(5, 10))
    
def test_start_stop_step():
    assert_equal(list(Range(5, 10, 2)), range(5, 10, 2))

def test_empty():
    assert_equal(list(Range(0, -10)), range(0, -10))

def test_empty_length():
    assert_equal(Range(0, -10).length, 0)
    
def test_length_not_aligned():
    assert_equal(Range(0, 11, 3).length, len(range(0, 11, 3)))

def test_reverse():
    assert_equal(list(Range(100)[::-1]), range(100)[::-1])
    
def test_length_negative_step():
    assert_equal(Range(9, -1, -1).length, len(range(9, -1, -1)))

def test_length_negative_step_not_aligned():
    assert_equal(Range(10, -1, -3).length, len(range(10, -1, -3)))

def test_index():
    assert_equal(Range(10, 100, 10)[3], 40)
    
def test_slice():
    assert_equal(Range(100)[10:20], Range(10, 20))
    assert_equal(Range(10, 100)[10:20], Range(20, 30))
    
def test_slice_multisteps():
    assert_equal(list(Range(100)[::2][::2]), range(100)[::2][::2])

def test_slice_neg_parts():
    assert_equal(Range(100)[-4:-1], Range(96, 99))
    
def test_slice_neg_parts2():
    assert_equal(list(Range(100)[-50:-1:3]), range(100)[-50:-1:3])

def test_slice_neg_parts3():
    assert_equal(list(Range(100)[-1:-50:-3]), range(100)[-1:-50:-3])

def test_overflow_slice():
    assert_equal(list(Range(100)[-200:]), range(100)[-200:])

def test_overflow_slice2():
    assert_equal(list(Range(100)[:-200:-1]), range(100)[:-200:-1])
        
def test_split():
    assert_equal(list(Range(5).split(2)), [Range(0, 3), Range(3, 5)])
       
if __name__ == '__main__':
    run()
