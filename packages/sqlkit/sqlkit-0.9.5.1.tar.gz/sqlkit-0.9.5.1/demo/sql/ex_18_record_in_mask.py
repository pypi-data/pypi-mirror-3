"""base/RecordInMask

Each row can be opened singularly by right-click on the row and choosing
"Show this record in a mask" or by using "record_in_mask" method of SqlTable.

in the same way you can open records on any foreign key, by just clicking on the 
foreign key and selecting "edit foreign key"

Here both of them have been requested programmatically
"""
        


t = SqlTable(model.Movie, dbproxy=db )
t.record_in_mask()
t.fkey_record_in_mask(field_name='director_id')

t.reload()
t.select_path(2)
