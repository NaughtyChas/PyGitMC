import wx
from frontend import MainFrame

if __name__ == '__main__':
    app = wx.App(False)
    
    # Set default font
    default_font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
    default_font.SetFaceName("Segoe UI")
    
    # Create and show main window
    frame = MainFrame(None)
    frame.Show()
    
    # Start main loop
    app.MainLoop()