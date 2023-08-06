"""base/different layout

a different layout with ReadOnly widgets and and exmple of == syntax that
prevents generation of label creation: in this case label is created
separatedly to force a different layout.
"""

lay = """
    ro=title
    date_release
    ro=director_id
    L=description
    TXS==description -
    """
from sqlkit.fields import VarcharField

t = SqlMask('movie', dbproxy=db, layout=lay)
t.reload()
