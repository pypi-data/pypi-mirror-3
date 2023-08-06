"""printing/related

You can also loop on related rows


"""

def prepare_context(printtool, context, template_name, sqlwidget):
    """
    substitue director's films as table objects
    """
    context['Table1'] = (sqlwidget.related.movies.records,)


lay = """
  first_name last_name
  nation
  o2m=movies - - -

"""

t = SqlMask(model.Director, layout=lay, dbproxy=db)
t.printing.add_menu_entry('Print to pdf', 'director-movies.odt', mode='pdf')
t.printing.add_menu_entry('Print to odt', 'director-movies.odt', mode='odt')
t.printing.connect('context-ready', prepare_context)
t.reload()


