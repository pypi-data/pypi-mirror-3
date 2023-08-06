import pandas as ps
from pandas.core.datetools import MonthEnd
from datetime import datetime

def budgetpanel_tocsv(p,path):
   
    method='m'

    if method=='m':
        grouped=p.groupby(lambda x: datetime(x.year,x.month,1)+MonthEnd())
    elif method=='q':
        grouped=p.groupby(lambda x: datetime(x.year,(((x.month-1)//3)+1)*3,1)+MonthEnd())
    else:
        grouped=p.groupby(lambda x: datetime(x.year,12,31))


    for grp,grp_p in grouped:
        print "GROUP %s " % grp
        print grp_p.minor_xs('actual').fillna(0).sum()
	    
	    
