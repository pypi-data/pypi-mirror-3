"""base/base import

these are the base import. All other examples skip the imports that are
granted by the way execfile is done in 'demo.py'.

The proxy is not strictly needed, it's just a way to pass metadata and session 
in a single argument

Table
-----
base editing mode: table view
When the first argument is a string, it triggets the reflection of the table
from the database. in this case the image is just rendered as string. Following
examples show how to change this.

NOT NULL fields are rendered with columns with italic font

Right-click on the record to see what you can do: delete, add a new record or
display the record in a Mask
"""

from sqlkit.widgets import SqlTable
from sqlkit.db import proxy
import model

db = proxy.DbProxy(bind="sqlite:///%s" % model.DB_FILE)


t = SqlTable('movie',    dbproxy=db, order_by='title', )
t.reload()

