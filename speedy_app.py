from talk import speak
import wx
import traceback
from speedy_frame import SpeedyFrame
from speedy_events import SpeedtestCompletedEvent, SpeedyEvents

class SpeedyError(Exception):
    def __init__(self, message):
        self.message = message
        print(message)
class SpeedyApp(wx.App):
    def OnInit(self):
        try:
            frame = SpeedyFrame(None, title="Speedy")
            events = SpeedyEvents(frame)
            frame.start_button.Bind(wx.EVT_BUTTON, events.on_start)
            frame.cancel_button.Bind(wx.EVT_BUTTON, events.on_cancel)
            frame.Show()
            return True
        except Exception as e:
            # Raise a custom SpeedyError with the exception details
            error_message = f"A runtime error occurred: {str(e)}\n\n{traceback.format_exc()}"
            raise SpeedyError(error_message)

if __name__ == "__main__":
    app = SpeedyApp()
    try:
        app.MainLoop()
    except SpeedyError as e:
        # Show an error message box with the exception details
        wx.MessageBox(str(e.message), "Speedy Runtime Error", wx.OK | wx.ICON_ERROR)
