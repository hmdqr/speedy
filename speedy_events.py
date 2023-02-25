import wx
import threading
import speedtest
from wx.lib.newevent import NewCommandEvent

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
        self.frame.output.SetValue("")
        self.frame.progress.SetValue(0)
        self.frame.set_cancelled(False)
        self.frame.speed = speedtest.Speedtest()
        print("Getting best server...")
        self.frame.speed.get_best_server()
        print("Done getting best server.")
        self.frame.thread = threading.Thread(target=self.run_speedtest, args=(self.frame,))
        self.frame.thread.start()
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

    def run_speedtest(self, frm):
        try:
            frm.speed.get_best_server()
            frm.update_status_label("Testing download speed...")
            frm.append_output_text("Testing download speed...\n")
            dl_speed = frm.speed.download(threads=None, callback=lambda c, t: frm.progress.SetValue(int(c / t * 100)))
            if frm.c:
                return
            frm.update_status_label("Testing upload speed...")
            frm.append_output_text("Testing upload speed...\n")
            ul_speed = frm.speed.upload(threads=None, callback=lambda c, t: frm.progress.SetValue(int(c / t * 100)))
            if frm.c:
                return
            frm.enable_start_button()
            frm.hide_cancel_button()
            frm.set_progress_value(100)
            out_text = f"Download speed: {dl_speed / 1_000_000:.2f} Mbps\nUpload speed: {ul_speed / 1_000_000:.2f} Mbps"
            frm.update_status_label(out_text)
            frm.append_output_text(out_text + "\n")
            frm.append_output_text("Speed test completed.\n")
            frm.set_focus_to_start_button()
            frm.set_start_button_label("Start")
            frm.start.Bind(wx.EVT_BUTTON, self.on_start)

            # Fire the SpeedtestCompletedEvent to notify the frame that the speed test is completed
            evt = SpeedtestCompletedEvent(ping_speed=0, download_speed=dl_speed, upload_speed=ul_speed)
            wx.PostEvent(frm, evt)

        except Exception as e:
            frm.enable_start_button()
            frm.hide_cancel_button()
            frm.set_progress_value(0)
            frm.update_status_label("An error occurred during the speed test. Please try again later.")
