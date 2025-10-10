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
