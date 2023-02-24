import wx
from speedy_frame import *
from speedy_events import *


class SpeedyApp(wx.App):
    def OnInit(self):
        self.frame = SpeedyFrame()
        self.frame.Show()
        return True

    def OnExit(self):
        self.frame.close()
        return 0


if __name__ == "__main__":
    app = SpeedyApp()
    app.MainLoop()

