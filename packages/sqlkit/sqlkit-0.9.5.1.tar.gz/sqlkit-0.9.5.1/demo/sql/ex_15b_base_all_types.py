"""base/table Views

Views in this context have nothing to do with SQL database views!

SqlTable has a 'main' view in which default TreeView is placed.
Further views can be added to represent different columns or the same columns in different layouts.

There is some magic in here in the sense that layout documentation is
somehow missing.  Each SqlTable has a default layout that has a TreeView
named TV=tree, so that you can find it in t.widgets['TV=tree'] (Note that
the extra 'S' you see in the layout is the ScrolledView that is added to
scroll the TreeView).

"""

lay = """

  {N
    { %text
        TVS=tree
    }
    { %numbers
        TVS=numbers
    }
    {
      %dates
        TVS=dates
    }
    }

"""


t = SqlTable(model.AllTypes, rows=5, dbproxy=db, layout=lay, field_list='varchar10,varchar200,text')
t.create_view(name='numbers', treeview=t.widgets['TV=numbers'], field_list='integer,varchar10,float,numeric')
t.create_view(name='dates', treeview=t.widgets['TV=dates'], field_list='date,datetime,interval')
t.reload()



