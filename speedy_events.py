import wx
from wx.lib.newevent import NewCommandEvent
import threading
import speedtest

# Define a custom event class for when the speed test is completed
SpeedtestCompletedEvent, EVT_SPEEDTEST_COMPLETED = NewCommandEvent()

EVT_SPEEDTEST_CANCELLED = wx.NewEventType()

class SpeedyEvents():
    def __init__(self, frame):
        self.frame = frame

    def on_start(self, event):
        print("on_start called")
        self.frame.disable_start_button()
        self.frame.show_cancel_button()
        self.frame.update_status_label("Testing, please wait...")
        self.frame.ping_text.SetLabel("")
        self.frame.set_progress_value(0)
        self.frame.set_cancelled(False)
        self.speed = speedtest.Speedtest()
        print("Getting best server...")
        self.speed.get_best_server()
        print("Done getting best server.")
        self.thread = threading.Thread(target=self.run_speedtest)
        self.thread.start()
        self.frame.append_output_text("Speed test started.\n")
        self.frame.set_focus_to_cancel_button()

        # Change the "Start" button to a "Cancel" button
        self.frame.start_button.SetLabel("Cancel")
        self.frame.start_button.Bind(wx.EVT_BUTTON, self.on_cancel)

    def on_cancel(self, event):
        frm = event.GetEventObject().GetParent()
        frm.c = True
        frm.cancel.Disable()
        frm.status.SetLabel("Test cancelled")
        frm.progress.SetValue(0)
        frm.start.Enable()
        frm.cancel.Hide()
        frm.append_output_text("Speed test cancelled.\n")
        frm.start.SetFocus()
        frm.start.SetLabel("Start")
        frm.start.Bind(wx.EVT_BUTTON, self.on_start)

        # Fire the SpeedtestCancelledEvent to notify the frame that the speed test is cancelled
        evt = wx.PyCommandEvent(EVT_SPEEDTEST_CANCELLED)
        wx.PostEvent(frm, evt)

    def run_speedtest(self):
        try:
            self.frame.set_progress_value(0)
            self.frame.append_output_text("Testing ping...\n")
            ping = self.speed.get_best_server()["latency"]
            self.frame.append_output_text("Ping: {} ms\n".format(ping))
            self.frame.update_status_label("Ping: {} ms".format(ping))
            self.frame.set_progress_value(33)
            if self.frame.c:
                return
            self.frame.append_output_text("Testing download speed...\n")
            download_speed = self.speed.download() / 1_000_000
            self.frame.append_output_text("Download speed: {:.2f} Mbps\n".format(download_speed))
            self.frame.download_text.SetLabel("{:.2f} Mbps".format(download_speed))
            self.frame.set_progress_value(66)
            if self.frame.c:
                return
            self.frame.append_output_text("Testing upload speed...\n")
            upload_speed = self.speed.upload() / 1_000_000
            self.frame.append_output_text("Upload speed: {:.2f} Mbps\n".format(upload_speed))
            self.frame.upload_text.SetLabel("{:.2f} Mbps".format(upload_speed))
            self.frame.set_progress_value(100)
            self.frame.hide_cancel_button()
            self.frame.set_start_button_label("Start")
            self.frame.start_button.Bind(wx.EVT_BUTTON, self.on_start)
        except Exception as e:
            print(e)
