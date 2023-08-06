def delta2dict( delta ):
    """return dictionary of delta"""
    return { 
        'year'   : delta.days / 365 ,
        'day'    : delta.days % 365 ,
        'hour'   : delta.seconds / 3600 ,
        'minute' : (delta.seconds / 60) % 60 ,
        'second' : delta.seconds % 60 ,
        'microsecond' : delta.microseconds
    }

def delta2human( delta, precision = 2 ):
    """return human readable delta string"""
    units = ( 'year', 'day', 'hour', 'minute', 'second', 'microsecond' )
    d = delta2dict( delta )
    hlist = [] 
    count = 0
    for unit in units:
        if count >= precision: break # met precision
        if d[ unit ] == 0: continue # skip 0's
        s = '' if d[ unit ] == 1 else 's' # handle plurals
        hlist.append( '%s %s%s' % ( d[unit], unit, s ) )
        count += 1
    return ', '.join( hlist )

def human( d1, precision = 2 ):
    """Pass datetime we will return human delta string"""
    from datetime import datetime
    d2 = datetime.now()
    delta = d2 - d1
    return delta2human( delta, precision ) 
  

def test():
    """Test and example usage"""
    from datetime import datetime
    d1 = datetime( 
      year = 2009, 
      month=5,
      day=4,
      hour=6,
      minute=54,
      second=33,
      microsecond=4000
     )
    d2 = datetime.now()
    delta = d2 - d1
    print 'This is just the ago.py test:'
    print delta2dict( delta )
    print 'Commented ' + delta2human( delta, 3 ) + ' ago'
    print 'Commented ' + human( d1 ) + ' ago'

if __name__ == "__main__": test()
