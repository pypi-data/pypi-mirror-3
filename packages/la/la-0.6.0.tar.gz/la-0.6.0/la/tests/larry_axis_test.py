"Test larry methods for proper handling of negative axis input"

# For support of python 2.5
from __future__ import with_statement

import numpy as np
from numpy.testing import assert_

from la import larry, nan
from la.util.testing import assert_larry_equal as ale

def lar():
    x = [[nan, nan],
         [1.0, 2.2],
         [3.4, 5.7]]
    label = [['a', 'b', 3], [0, 1]]     
    return larry(x, label)

#       Method          Parameters
mts = [('any'        ,  ['axis']),
       ('all'        ,  ['axis']),
       ('cumprod'    ,  ['axis']),
       ('cumsum'     ,  ['axis']),
       ('cut_missing',  [0.1, 'axis']),                                           
       ('demean'     ,  ['axis']), 
       ('demedian'   ,  ['axis']),     
       ('flipaxis'   ,  ['axis']),                                                                                               
       ('getlabel'   ,  ['axis']),
       ('keep_label' ,  ['>', 0, 'axis']),
       ('labelindex' ,  [0, 'axis']),
       ('lag'        ,  [1, 'axis']),
       ('lastrank'   ,  ['axis']),
       ('lastrank'   ,  ['axis', 10]),
       ('maplabel'   ,  [str, 'axis']),
       ('max'        ,  ['axis']),
       ('maxlabel'   ,  ['axis']),
       ('mean'       ,  ['axis']),
       ('geometric_mean',  ['axis']),
       ('median'     ,  ['axis']),
       ('min'        ,  ['axis']),
       ('minlabel'   ,  ['axis']),       
       ('movingrank' ,  [2, 'axis']),
       ('move_sum'   ,  [1, 'axis']),
       ('movingsum_forward', [1, 0, 'axis']),
       ('prod'       ,  ['axis']), 
       ('pull'       ,  [0, 'axis']),      
       ('ranking'    ,  ['axis']), 
       ('ranking'    ,  ['axis', '0,N-1']),       
       ('sortaxis'   ,  ['axis']),      
       ('std'        ,  ['axis']),       
       ('sum'        ,  ['axis']), 
       ('take'       ,  [[1,0], 'axis']),       
       ('vacuum'     ,  ['axis']), 
       ('var'        ,  ['axis']),       
       ('std'        ,  ['axis']),         
       ('zscore'     ,  ['axis']),                             
      ]
                        
def test_negative_axis(): 
    "Test larry methods for proper handling of negative axis input"      
    for attr, parameters in mts:
        method = getattr(lar(), attr)
        p = list(parameters)
        p[p.index('axis')] = -1
        with np.errstate(invalid='ignore', divide='ignore'):
            actual = method(*p)
        p = list(parameters)
        p[p.index('axis')] = 1        
        with np.errstate(invalid='ignore', divide='ignore'):
            desired = method(*p)
        msg = "method '" + attr + "' failed axis=-1 larry test"
        if type(actual) == larry:
            yield ale, actual, desired, msg     
        else:
            yield assert_, actual == desired, msg
             

