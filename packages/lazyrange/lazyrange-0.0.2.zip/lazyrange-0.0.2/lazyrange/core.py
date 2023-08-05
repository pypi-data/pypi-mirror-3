""" A very lazy Range object """

def indices(start, stop, step, length):
    """ A non-overflow version of slice.indices """
    
    # this is harder to get right than you might think
    
    if step is None:
        step = 1
    else:
        if step == 0:
            raise ValueError('step must not be 0')
        
    if start is None:
        start = length-1 if step < 0 else 0
    else:
        if start < 0:
            start += length
        if start < 0:
            start = -1 if step < 0 else 0
        if start >= length:
            start = length-1 if step < 0 else length

    if stop is None:
        stop = -1 if step < 0 else length
    else:
        if stop < 0:
            stop += length
        if stop < 0:
            stop = -1 if step < 0 else 0
        if stop >= length:
            stop = length-1 if step < 0 else length

    return start, stop, step
    
class Range(object):
    """ A very lazy Range object """
    
    def __init__(self, start, stop=None, step=1):
        """ Range([start=0,] stop[, step=1]) """
        
        if stop is None:
            start, stop = 0, start
        if not step:
            raise ValueError('step must not be 0')

        self.start = start
        self.stop = stop
        self.step = step
        self.length = Range.compute_length(start, stop, step)

    @staticmethod
    def compute_length(start, stop, step):
        """ Return number of items of Range(start, stop, step). """
        if (step < 0 and stop >= start) or (step > 0 and start >= stop):
            return 0
        if step < 0:
            return (stop-start+1)//step+1
        else:
            return (stop-start-1)//step+1

    def __len__(self):
        return self.length
    
    def __eq__(self, other):
        return (isinstance(other, Range) 
            and self.start == other.start 
            and self.length == other.length
            and self.step == other.step
        )

    def __ne__(self, other):
        return not self == other

    def __iter__(self):
        start, stop, step = self.start, self.stop, self.step
        if step > 0:
            while start < stop:
                yield start
                start += step
        elif step < 0:
            while start > stop:
                yield start
                start += step

    def compute_item(self, index):
        """ Return item at index regardless of whether index belongs to 
        range(length) or not.
        
        compute_item(-1) will return the value before start,
        compute_item(length) wuill return the stop value,
        they can be thought as boundary value of the range. """
        
        return self.start + index*self.step

    def compute_slice(self, sliceobj):
        """ Return a new Range object, which is a slicing of current range, 
        according to sliceobj. """
        
        start, stop, step = indices(
            sliceobj.start, 
            sliceobj.stop, 
            sliceobj.step, 
            self.length,
        )
        return Range(
            self.compute_item(start), 
            self.compute_item(stop), 
            step*self.step,
        )
                
    def __getitem__(self, index):
        if isinstance(index, slice):
            return self.compute_slice(index)
        elif isinstance(index, (int, long)):
            if -self.length <= index < self.length:
                return self.compute_item(index % self.length)
            else:
                raise IndexError(index)
        else:
            raise TypeError(
                'Expected slice/int/long, got {}'.format(repr(index)))

    def __reversed__(self):
        return self[::-1]
    
    def __contains__(self, value):
        start, stop, step = self.start, self.stop, self.step
        if ((step > 0 and start <= value < stop) or
            (step < 0 and start >= value > stop)):
            return (value-start) % step == 0
        else:
            return False
            
    def __repr__(self):
        if self.step == 1:
            return 'Range({}, {})'.format(self.start, self.stop)
        else:
            return 'Range({}, {}, {})'.format(self.start, self.stop, self.step)

    def index(self, value, start=None, stop=None):
        """ R.index(value, [start, [stop]]) -> integer
        Return first index of value.
        Raises ValueError if the value is not present. """
        
        if value not in self[start:stop]:
            raise ValueError('value {} is out of {}'.format(value, self))
        return (value-self.start)//self.step

    def count(self, value):
        """ Return 1 if `value` is found in the range, otherwise return 0.
        
        This method is presented because .count() is required for 
        issubclass(range, collections.abc.Sequence)
        """
        return 1 if value in self else 0
        
    def split(self, cols=2):
        """ Split the range into roughly equal-sized pieces """
        start = 0
        for i in range(cols):
            stop = start + self[i::cols].length
            yield self[start:stop]
            start = stop

