"""base/base genre


"""

from sqlkit.widgets import SqlTable
from sqlkit.db import proxy
import model

db = proxy.DbProxy(bind="sqlite:///%s" % model.DB_FILE)


t = SqlTable(model.Genre,    dbproxy=db )
t.reload()

