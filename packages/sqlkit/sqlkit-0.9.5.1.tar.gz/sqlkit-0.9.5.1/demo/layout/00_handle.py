"""Bricks/handleBox

"""

lay = """
  {H {Z  { uno due tre
         b=gtk-ok}
      }
     {Z  { abc def
         b=gtk-cancel}
     }
}
"""

l = Layout(lay, opts='s')
w = l.show()

