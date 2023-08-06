"""printing/preparing Context

You can customize the context you pass to the PrintTool eather subclassing
and overriding prepare_context or connecting to signal 'context-ready'
"""

from sqlkit.misc.printing import PrintTool

class MyPrinter(PrintTool):

    def prepare_context(self, context):
        """
        substitue director's films as table objects
        """
        context.translate['d'] = 'director'
        context.translate['nation'] = 'director.nation'
        return context

    

t = SqlTable(model.Movie, dbproxy=db)
t.printing = MyPrinter(t)
t.printing.add_menu_entry('Print to pdf', 'movies-translate.odt', mode='pdf',
                          accel="<alt>p",
                          tip="Generate a pdf file with these movies")
t.printing.add_menu_entry('Print to odt', 'movies-translate.odt', mode='odt',
                          tip="Generate an odt file with these movies")
t.reload()


