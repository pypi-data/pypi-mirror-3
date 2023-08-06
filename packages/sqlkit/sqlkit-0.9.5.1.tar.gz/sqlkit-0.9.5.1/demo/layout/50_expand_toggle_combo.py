"""more/expander

'>>' forces expanded position

"""

lay = """
  {>>.main

      {>>|.a  t=mare      t=montagna
        t=campagna  t=citta
      }

      {>.b  C=mare2      Ce=montagna2
          C=campagna2  Ce=citta2
      }
  }
"""


l = Layout(lay,opts="V")

w = l.show()

