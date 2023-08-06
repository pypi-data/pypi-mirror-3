"""Bricks/check-radio

radiobuttons are grouped by the group parameter. A radiobutton whose name has
a /group1 part is aggregated to group1. only one radiobutton at a time can be
switched on. 
"""


lay = """
   c=check
   r=radio1  r=radio2/radio1
"""


l = Layout(lay)
w = l.show()


        
    
