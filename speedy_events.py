from talk import speak
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
        self.speedtest = speedtest.Speedtest()

    def on_start(self, event):
        print("on_start called")
        speak("on_start called")
        self.frame.disable_start_button()
        self.frame.show_cancel_button()
        self.frame.update_status_label("Testing, please wait...")
        speak("Testing, please wait...")
        self.frame.update_status_label("")
        self.frame.set_cancelled(False)
        self.thread = threading.Thread(target=self.run_speedtest)
        self.thread.start()
        self.frame.update_status_label("Speed test started.\n")
        self.frame.set_focus_to_cancel_button()

        # Change the "Start" button to a "Cancel" button
        self.frame.start_button.SetLabel("Cancel")
        self.frame.start_button.Bind(wx.EVT_BUTTON, self.on_cancel)
        speak("Speed test started.")
    def on_cancel(self, event):
        self.frame.set_cancelled(True)
        self.frame.cancel_button.Disable()
        self.frame.update_status_label("Test cancelled")
        self.frame.set_progress_value(0)
        self.frame.enable_start_button()
        self.frame.hide_cancel_button()
        self.frame.update_status_label("Speed test cancelled.\n")
        self.frame.set_focus_to_start_button()
        self.frame.set_start_button_label("Start")
        self.frame.start_button.Bind(wx.EVT_BUTTON, self.on_start)
        # Fire the SpeedtestCancelledEvent to notify the frame that the speed test is cancelled
        evt = wx.PyCommandEvent(EVT_SPEEDTEST_CANCELLED)
        wx.PostEvent(self.frame, evt)
        speak("test canceled...")
    def run_speedtest(self):
        try:
            self.frame.set_progress_value(0)

            if self.frame.c:
                return
            self.frame.update_status_label("Testing download speed...\n")
            speak ("Testing download speed...\n")
            download_speed = self.speedtest.download() / 1_000_000
            self.frame.update_status_label("Download speed: {:.2f} Mbps\n".format(download_speed))
            speak("Download speed: {:.2f} Mbps\n".format(download_speed))
            self.frame.download_text.SetLabel("{:.2f} Mbps".format(download_speed))
            self.frame.set_progress_value(66)
            if self.frame.c:
                return
            self.frame.update_status_label("Testing upload speed...\n")
            speak("Testing upload speed...\n")
            upload_speed = self.speedtest.upload() / 1_000_000
            self.frame.update_status_label("Upload speed: {:.2f} Mbps\n".format(upload_speed))
            speak("Upload speed: {:.2f} Mbps\n".format(upload_speed))
            self.frame.upload_text.SetLabel("{:.2f} Mbps".format(upload_speed))
            self.frame.set_progress_value(100)
            self.frame.hide_cancel_button()
            self.frame.set_start_button_label("Start")
            self.frame.start_button.Bind(wx.EVT_BUTTON, self.on_start)
        except Exception as e:
            speak(e)
            print(e)
