
def bin(start, end, offsets=(512+64+8+1, 64+8+1, 8+1, 1, 0), _first_shift=17, _next_shift=3):
    """ calculate bin for range queries
    
        See http://genomewiki.tables.edu/index.php/Bin_indexing_system
    """
    start_bin, end_bin = start, end - 1 
    start_bin >>= _first_shift
    end_bin >>= _first_shift
    
    for offset in offsets:
        if (start_bin == end_bin): return offset + start_bin
        start_bin >>= _next_shift
        end_bin >>= _next_shift
        
    raise Exception('unable to get bin for range (%s, %s)' % (start, end))
