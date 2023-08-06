"""
General uimanager description. Divided in:

  1. general purpose
  2. table only
  3. mask only
  4. browse only  (when a mask is only ment to show fixed data)
  5. print (not ready)
  6. debug (gtk + table browse)
"""

GENERAL_UI = '''
  <menubar name="Main">
     <menu action="File">
        <menuitem action="Filters"/>
        <separator name="sep1" />

        <menuitem action="New"/>
        <menuitem action="Save"/>
        <placeholder name="Save-as">
        </placeholder>

        <separator name="sepprint" />
        <placeholder name="Print-ph">
        </placeholder>

        <separator name="sep2" />
        <placeholder name="Export">
        </placeholder>
        <menuitem action="Quit" />
     </menu>

     <menu action="Modify">
     </menu>

     <menu action="Go">
     </menu>

     <menu action="Tools">
     <menuitem action="PendingDifferences"/>
     </menu>

     <menu action="Help">
        <menuitem action="About"/>
     </menu>

  </menubar>
  <toolbar name="TbMain">
    <toolitem  action="Save" />
    <placeholder name="Save-as">
    </placeholder>
    <toolitem  action="New" />
  </toolbar>
'''

PRINT_UI = '''
  <menubar name="Main">
     <menu action="File">
       <placeholder name="Print-ph" >
          <menu action="Print">
          </menu>
       </placeholder>  
     </menu>

  </menubar>

'''

TABLE_UI = '''
  <menubar name="Main">
     <menu action="File">
        <placeholder name="Export">
           <menuitem action="Export"/>
        </placeholder>
     </menu>

     <menu action="Modify">
        <menuitem action="Zoom-fit" />
        <menu action="ShowColumns" />
        <menu action="HideColumns" />
     </menu>
  </menubar>

'''
TREEPOPUP = '''
  <popup name="TreePopup">
        <separator name="sep_1" />
        <menuitem action="MaskView" />
        <menuitem action="MaskViewFKey" />
        <menuitem action="Duplicate" />
        <menuitem action="New" />
        <menuitem action="NewChild" />
        <menuitem action="UploadImage" />
        <menuitem action="DeleteFile" />
        <menuitem action="UploadFile" />
        <menuitem action="ShowFile" />
        <menuitem action="SaveFile" />
        <separator name="sep_cols" />
        <placeholder name="Columns"/>
        <separator name="sep_del" />
        <menuitem action="RecordDelete" />
  </popup>
'''

MASK_UI = '''
  <menubar name="Main">
     <menu action="File">
        <placeholder name="Save-as">
            <menuitem action="Save-as"/>
        </placeholder>
     </menu>
     <menu action="Modify">
        <menuitem action="Undo" position="top" />
        <menuitem action="RefreshRecord" position="top" />
     </menu>
     
  </menubar>
  <toolbar name="TbMain">
    <placeholder name="Save-as">
      <toolitem action="Save-as"/>
    </placeholder>
  </toolbar>
'''

BROWSE_UI = '''
  <menubar name="Main">
     <menu action="File">
           <menuitem action="Filters" position="top" />
           <separator name="sep3" />
     </menu>

     <menu action="Modify">
        <menuitem action="Delete" position="top" />
     </menu>
     <menu action="Go">
        <menuitem action="Reload" />
        <menuitem action="Forward" />
        <menuitem action="Back" />
     </menu>
  </menubar>
  <toolbar name="TbMain">
        <toolitem  action="Delete" />
        <toolitem action="Reload" />
        <toolitem action="Back" />
        <toolitem action="Forward" />
  </toolbar>

'''

DEBUG_UI = '''
  <menubar name="Main">
     <menu action="Tools">
        <menuitem action="Gtk-tree"/>
     </menu>

  </menubar>
'''

