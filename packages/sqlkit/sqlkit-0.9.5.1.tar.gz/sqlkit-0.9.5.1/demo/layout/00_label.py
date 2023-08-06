"""Bricks/label con dim Table e VBox

a simple label is obtained w/ a l= flag
A label of fixed width is obtained with a trailing :width

"""

lay = """
   # comment
   l=label:<
   ae=short_lbl:2
   l=label2:>
   e=long_lbl
   ae=short_lbl2:2>
"""

lt = Layout(lay, opts='T', title="Table")
lt.prop('e=short_lbl','xalign',1)
#lt.xml("/tmp/g.glade")
#lt.prop('e=short_lbl2','max-length',2)
w = lt.show()
#print w.keys()

# lv = Layout(lay, opts='V', title="VBox")
# lv.prop('e=short_lbl2','max-length',2)
# lv.xml("/tmp/g.glade")
# w = lv.show()

w['Window'].show_all()

# tour.py si aspetta che ogni esempio inizializzi l, xml e ogni altra
# propriet`a viene fatta guardando l... quindi


l = lt 
#l = lv

