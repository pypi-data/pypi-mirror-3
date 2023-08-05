
class Range(object):
    """ A very lazy Range object """
    
    def __init__(self, start, stop=None, step=1):
        ''' range([start=0,] stop[, step=1]) '''
        
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
        if (step < 0 and stop >= start) or (step > 0 and start >= stop):
            return 0
        if step < 0:
            return (stop-start+1)//step+1
        else:
            return (stop-start-1)//step+1

    #
    # XXX: Don't implement __len__, it must return C integer which is not compatible with large range
    #
    
    #
    # XXX: Totol ordering ???
    #
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

    @staticmethod
    def indices(slice, length):
        """ A non-overflow version of slice.indices """
        start = slice.start
        stop = slice.stop
        step = slice.step
        
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

    def compute_item(self, i):
        return self.start + i*self.step

    def compute_slice(self, slice):
        start, stop, step = Range.indices(slice, self.length)
        return Range(self.compute_item(start), self.compute_item(stop), step*self.step)
                
    def __getitem__(self, index):
        if isinstance(index, slice):
            return self.compute_slice(index)
        elif isinstance(index, (int, long)):
            if -self.length <= index < self.length:
                return self.compute_item(index % self.length)
            else:
                raise IndexError(index)
        else:
            raise TypeError('Expected slice/int/long, got {}'.format(repr(index)))

    def __reversed__(self):
        return self[::-1]
    
    def __contains__(self, x):
        start, stop, step = self.start, self.stop, self.step
        if ((step > 0 and start <= x < stop) or
            (step < 0 and start >= x > stop)):
            return (x-start) % step == 0
        else:
            return False
            
    def __repr__(self):
        if self.step == 1:
            return 'Range({}, {})'.format(self.start, self.stop)
        else:
            return 'Range({}, {}, {})'.format(self.start, self.stop, self.step)

    def index(self, value):
        if value not in self:
            raise ValueError('value {} is out of {}'.format(value, self))
        return (value-self.start)//self.step

    def count(self, value):
        # .count() is required for issubclass(range, collections.abc.Sequence)
        return 1 if value in self else 0
        
    def split(self, cols=2):
        start = 0
        for i in range(cols):
            stop = start + self[i::cols].length
            yield self[start:stop]
            start = stop

