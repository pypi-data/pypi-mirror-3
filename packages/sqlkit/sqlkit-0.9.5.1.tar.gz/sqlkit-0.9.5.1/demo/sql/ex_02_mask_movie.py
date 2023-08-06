"""base/movie mask

base editing mode: mask view

Note how simple it is to define the layout. You just write the name of the
field and a label + entry will be displayed. Each database type has a
different widget that is determined by SqlMask by introspection. You can
force it as for 'image' and 'description' in the second example if
you want a different renderer (eg.: the Text instead of the Entry) or if you
want to get rid of the label (via the double '=='). Curly braces can be used
to group a set of fields.


Double click on the search icon in director_id field to mimic an 'enum' field,
i.e. all choices will be shown.

"""

## Very simple, no layout definition -> a default layout is created 
t1 = SqlMask(model.Movie, dbproxy=db)
t1.reload()


## Let's define a layout with the image on the left
lay = """
     img==image:140.200  {|
         title
         date_release
         TXS=description 
         director_id
    }
    """
t = SqlMask(model.Movie, dbproxy=db, layout=lay)
t.gui_fields.image.default_size = 250,250
t.reload()
