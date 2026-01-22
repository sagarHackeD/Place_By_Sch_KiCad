import os
import wx
import threading


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
    def __init__(self, parent, on_advance=None, on_place=None, on_clean=None):
        super().__init__(parent, title="Place By Sch", size=(300, 200))
        self.on_advance = on_advance
        self.on_place = on_place
        self.on_clean = on_clean

        icon = wx.Icon(
            os.path.join(os.path.dirname(__file__), "icon.png"), wx.BITMAP_TYPE_PNG
        )
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

        # choices = ["Apple", "Banana", "Orange", "Mango"]
        # self.dropdown = wx.Choice(self, choices=choices)

        # vbox.Add(self.dropdown, 0, wx.CENTER)

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

        advance_btn.Bind(wx.EVT_BUTTON, lambda e: self.handle_advance())
        place_btn.Bind(wx.EVT_BUTTON, lambda e: self.handle_place())
        clean_btn.Bind(wx.EVT_BUTTON, lambda e: self.handle_clean())
        cancel_btn.Bind(wx.EVT_BUTTON, lambda e: self.EndModal(wx.ID_CANCEL))

    def handle_advance(self):
        # Run the advance callback in a background thread and
        # pulse the gauge via a wx.Timer so the UI stays responsive.
        if not callable(self.on_advance):
            return

        # immediate visual feedback
        self.gauge.Pulse()

        # set up a timer to keep pulsing the gauge while work runs
        self._advance_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._on_advance_timer, self._advance_timer)
        self._advance_timer.Start(100)

        def worker():
            try:
                self.on_advance(self)
            except Exception:
                pass
            finally:
                wx.CallAfter(self._finish_advance)

        t = threading.Thread(target=worker, daemon=True)
        t.start()

    def _on_advance_timer(self, _event):
        try:
            self.gauge.Pulse()
        except Exception:
            pass

    def _finish_advance(self):
        try:
            if hasattr(self, "_advance_timer") and self._advance_timer.IsRunning():
                self._advance_timer.Stop()
                try:
                    self.Unbind(wx.EVT_TIMER, handler=self._on_advance_timer, source=self._advance_timer)
                except Exception:
                    pass
        finally:
            try:
                self.EndModal(wx.ID_OK)
            except Exception:
                pass

    def handle_place(self):
        # Run the place callback in a background thread and
        # pulse the gauge via a wx.Timer so the UI stays responsive.
        if not callable(self.on_place):
            return

        # immediate visual feedback
        self.gauge.Pulse()

        # set up a timer to keep pulsing the gauge while work runs
        self._place_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._on_place_timer, self._place_timer)
        self._place_timer.Start(100)

        def worker():
            try:
                self.on_place(self)
            except Exception:
                pass
            finally:
                wx.CallAfter(self._finish_place)

        t = threading.Thread(target=worker, daemon=True)
        t.start()

    def _on_place_timer(self, _event):
        try:
            self.gauge.Pulse()
        except Exception:
            pass

    def _finish_place(self):
        try:
            if hasattr(self, "_place_timer") and self._place_timer.IsRunning():
                self._place_timer.Stop()
                try:
                    self.Unbind(wx.EVT_TIMER, handler=self._on_place_timer, source=self._place_timer)
                except Exception:
                    pass
        finally:
            try:
                self.EndModal(wx.ID_OK)
            except Exception:
                pass

    def handle_clean(self):
        # provide immediate feedback
        self.gauge.Pulse()
        if callable(self.on_clean):
            try:
                self.on_clean(self)
                self.EndModal(wx.ID_OK)
            except Exception:
                # Avoid crashing the dialog if callback raises
                pass

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

        icon = wx.Icon(
            os.path.join(os.path.dirname(__file__), "icon.png"), wx.BITMAP_TYPE_PNG
        )
        self.SetIcon(icon)

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
