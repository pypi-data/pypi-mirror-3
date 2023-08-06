"""printing/pdf

You can print to a file in both .pdf and .odt format if you have uno
installed (it comes with openoffice) and can use an openoffice server.

NOTE:
This sample will *fail* if you cannot start an openoffice server
or if you dont have the 'uno' module from openoffice.

"""

def debug_context(printtool, context, template_name, sqlwidget):
    print "CONTEXT:", context

t = SqlTable(model.Movie, dbproxy=db)
t.printing.add_menu_entry('Print to pdf', 'movies.odt', mode='pdf',
                          accel="<alt>p",
                          tip="Generate a pdf file with these movies")
t.printing.connect('context-ready', debug_context)
t.reload()


