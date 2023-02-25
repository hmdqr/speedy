import wx
from speedy_frame import SpeedyFrame
from speedy_events import SpeedtestCompletedEvent, SpeedyEvents
class SpeedyApp(wx.App):
    def OnInit(self):
        frame = SpeedyFrame(None, title="Speedy")
        events = SpeedyEvents(frame)
        frame.start_button.Bind(wx.EVT_BUTTON, events.on_start)
        frame.cancel_button.Bind(wx.EVT_BUTTON, events.on_cancel)
        frame.Show()
        return True

if __name__ == "__main__":
    app = SpeedyApp()
    app.MainLoop()
