import wx


def ask_to_run():
    if (
        wx.MessageBox(
            "This will move all selected and not locked footprints to match the schematic positions. Continue?",
            "Place By Schematics",
            wx.ICON_QUESTION | wx.YES_NO,
        )
        == wx.YES
    ):
        return True


def debug_msg(msg):
    """Show a debug message box"""
    dlg = wx.MessageDialog(
        None,
        str(msg),
        "Debug Message",
        wx.OK | wx.ICON_INFORMATION,
    )
    dlg.ShowModal()  # Show the dialog
    dlg.Destroy()  # Destroy the dialog after use


class ActionDialog(wx.Dialog):
    def __init__(self, parent):
        super().__init__(parent, title="Place By Sch", size=(300, 150))

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(wx.StaticText(self, label="This will move all selected and not locked footprints to match the schematic positions.\nChoose an action"), 0, wx.ALL | wx.CENTER, 10)

        hbox = wx.BoxSizer(wx.HORIZONTAL)

        advance_btn = wx.Button(self, label="Advance")
        place_btn = wx.Button(self, label="Place")
        cancel_btn = wx.Button(self, label="Cancel")

        hbox.Add(advance_btn, 1, wx.ALL, 5)
        hbox.Add(place_btn, 1, wx.ALL, 5)
        hbox.Add(cancel_btn, 1, wx.ALL, 5)

        vbox.Add(hbox, 0, wx.CENTER)
        self.SetSizerAndFit(vbox)

        advance_btn.Bind(wx.EVT_BUTTON, lambda e: self.EndModal(1))
        place_btn.Bind(wx.EVT_BUTTON, lambda e: self.EndModal(2))
        cancel_btn.Bind(wx.EVT_BUTTON, lambda e: self.EndModal(wx.ID_CANCEL))


class CheckListDialog(wx.Dialog):
    def OnAllLayers(self, _):
        for i in range(self.sheets.GetCount()):
            self.sheets.Check(i, True)

    def OnNoLayers(self, _):
        for i in range(self.sheets.GetCount()):
            self.sheets.Check(i, False)

    def __init__(self, parent,choices):
        super().__init__(parent, title="Select Sheets to place", size=(400, 500))

        vbox = wx.BoxSizer(wx.VERTICAL)

        # CheckListBox
        vbox.Add(wx.StaticText(self, label="Sheets"), 0, wx.ALL, 5)
        self.sheets = wx.CheckListBox(self, choices=choices)
        vbox.Add(self.sheets, 1, wx.EXPAND | wx.ALL, 5)

        allLayersBtn = wx.Button(self, label='All layers')
        self.Bind(wx.EVT_BUTTON, self.OnAllLayers, id=allLayersBtn.GetId())

        noLayersBtn = wx.Button(self, label='No layers')
        self.Bind(wx.EVT_BUTTON, self.OnNoLayers, id=noLayersBtn.GetId())
        
        vbox.Add(allLayersBtn, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        vbox.Add(noLayersBtn, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        # OK / Cancel buttons
        btns = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        vbox.Add(btns, 0, wx.ALIGN_CENTER | wx.ALL, 10)



        self.SetSizer(vbox)

    def get_values(self):
        return {
            "sheets": [
                self.sheets.GetString(i) for i in self.sheets.GetCheckedItems()
            ]
        }

