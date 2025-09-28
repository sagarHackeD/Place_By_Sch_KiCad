import wx

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