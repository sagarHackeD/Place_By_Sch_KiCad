import os
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
        super().__init__(parent, title="Place By Sch", size=(300, 200))

        icon = wx.Icon(os.path.join(os.path.dirname(__file__), "icon.png"), wx.BITMAP_TYPE_PNG)
        self.SetIcon(icon)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(
            wx.StaticText(
                self,
                label="This will move all selected and not locked footprints to match the schematic positions.\nChoose an action",
            ),
            0,
            wx.ALL | wx.CENTER,
            10,
        )

        # Add progress bar
        # self.progress = wx.Gauge(self, range=100, style=wx.GA_HORIZONTAL)
        # vbox.Add(self.progress, 0, wx.EXPAND | wx.ALL, 10)

        self.gauge = wx.Gauge(self, range=100)
        vbox.Add(self.gauge, flag=wx.ALL | wx.CENTER | wx.EXPAND, border=10)

        hbox = wx.BoxSizer(wx.HORIZONTAL)

        hboxc = wx.BoxSizer(wx.HORIZONTAL)

        self.checkbox_locks = wx.CheckBox(self, label="Override locks")
        self.checkbox_selection = wx.CheckBox(self, label="Override selection")

        hboxc.Add(self.checkbox_locks, 0, wx.ALL, 5)
        hboxc.Add(self.checkbox_selection, 0, wx.ALL, 5)

        clean_btn = wx.Button(self, label="Clean")
        advance_btn = wx.Button(self, label="Advance")
        place_btn = wx.Button(self, label="Place")
        cancel_btn = wx.Button(self, label="Cancel")

        hbox.Add(clean_btn, 1, wx.ALL, 5)
        hbox.Add(advance_btn, 1, wx.ALL, 5)
        hbox.Add(place_btn, 1, wx.ALL, 5)
        hbox.Add(cancel_btn, 1, wx.ALL, 5)

        vbox.Add(hboxc, 0, wx.CENTER)
        vbox.Add(hbox, 0, wx.CENTER)
        self.SetSizerAndFit(vbox)

        advance_btn.Bind(wx.EVT_BUTTON, lambda e: self.EndModal(1))
        place_btn.Bind(wx.EVT_BUTTON, lambda e: self.EndModal(2))
        clean_btn.Bind(wx.EVT_BUTTON, lambda e: self.EndModal(3))
        cancel_btn.Bind(wx.EVT_BUTTON, lambda e: self.EndModal(wx.ID_CANCEL))

    def get_checkbox_values(self):
        return [
            self.checkbox_locks.GetValue(),
            self.checkbox_selection.GetValue(),
        ]


class CheckListDialog(wx.Dialog):
    def OnAllLayers(self, _):
        for i in range(self.sheet_checkboxs.GetCount()):
            self.sheet_checkboxs.Check(i, True)

    def OnNoLayers(self, _):
        for i in range(self.sheet_checkboxs.GetCount()):
            self.sheet_checkboxs.Check(i, False)

    def __init__(
        self,
        parent,
        choices,
        title="Select Sheets to place",
        size=(300, 500),
    ):
        super().__init__(parent, title=title, size=size)
        choices = choices or []

        vbox = wx.BoxSizer(wx.VERTICAL)

        # First CheckListBox
        vbox.Add(wx.StaticText(self, label="Sheets"), 0, wx.ALL, 5)
        self.sheet_checkboxs = wx.CheckListBox(self, choices=choices)
        vbox.Add(self.sheet_checkboxs, 1, wx.EXPAND | wx.ALL, 5)
        # self.sheet_checkboxs.SetChecked(0, True)  # Pre-check Python

        hbox = wx.BoxSizer(wx.HORIZONTAL)

        allLayersBtn = wx.Button(self, label="All layers")
        self.Bind(wx.EVT_BUTTON, self.OnAllLayers, id=allLayersBtn.GetId())

        noLayersBtn = wx.Button(self, label="No layers")
        self.Bind(wx.EVT_BUTTON, self.OnNoLayers, id=noLayersBtn.GetId())

        hbox.Add(allLayersBtn, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        hbox.Add(noLayersBtn, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        vbox.Add(hbox, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        # vbox.Add(noLayersBtn, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        # OK / Cancel buttons
        btns = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        vbox.Add(btns, 0, wx.ALIGN_CENTER | wx.ALL, 10)

        self.SetSizer(vbox)

    def get_values(self):
        return [
            self.sheet_checkboxs.GetString(i)
            for i in self.sheet_checkboxs.GetCheckedItems()
        ]


class ProgressDialog(wx.Dialog):
    def __init__(self, parent):
        super().__init__(parent, title="Processing...", size=(300, 150))

        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        self.gauge = wx.Gauge(panel, range=100, size=(250, 25))
        vbox.Add(self.gauge, 0, wx.ALL | wx.CENTER, 15)

        panel.SetSizer(vbox)

        self.gauge.Pulse()
