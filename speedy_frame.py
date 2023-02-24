import wx
import threading
import speedtest
from speedy_events import *


class SpeedyFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Speedy", size=(300, 150))

        # Create controls
        self.status = wx.StaticText(self, label="")
        self.output = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY, name="Speedy Results")
        self.progress = wx.Gauge(self, range=100)
        self.start = wx.Button(self, label="Start", name="Start Speedy")
        self.cancel = wx.Button(self, label="Cancel", style=wx.BU_LEFT, name="Cancel Speedy")

        # Set sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.status, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        sizer.Add(self.output, 1, wx.EXPAND | wx.ALL, 10)
        sizer.Add(self.progress, 0, wx.EXPAND | wx.ALL, 10)
        sizer.Add(self.start, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        sizer.Add(self.cancel, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        self.SetSizer(sizer)

        # Bind events
        self.start.Bind(wx.EVT_BUTTON, on_start)
        self.cancel.Bind(wx.EVT_BUTTON, on_cancel)

        # Initialize variables
        self.speed = None
        self.thread = None
        self.cancelled = False

        # Set initial control states
        self.start.Enable()
        self.cancel.Hide()
        self.start.SetFocus()

    def update_status_label(self, text):
        self.status.SetLabel(text)

    def append_output_text(self, text):
        self.output.AppendText(text)

    def update_progress_bar(self, current, total, **kwargs):
        percent = int(current / total * 100)
        wx.CallAfter(self.progress.SetValue, percent)

    def enable_start_button(self):
        self.start.Enable()

    def disable_start_button(self):
        self.start.Disable()

    def show_cancel_button(self):
        self.cancel.Show()

    def hide_cancel_button(self):
        self.cancel.Hide()

    def set_focus_to_start_button(self):
        self.start.SetFocus()

    def set_cancelled(self, cancelled):
        self.cancelled = cancelled

    def is_cancelled(self):
        return self.cancelled

    def close(self):
        if self.thread:
            self.thread.join()
        self.Destroy()

