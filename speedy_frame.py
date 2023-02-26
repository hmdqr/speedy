import sys
sys.dont_write_bytecode = True
from talk import speak
from pubsub import pub
import wx
import threading
import speedtest

class SpeedyFrame(wx.Frame):
    def __init__(self, parent, title):
        super().__init__(parent, title=title, size=(400, 250))

        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        st1 = wx.StaticText(panel, label="Ping:")
        hbox1.Add(st1, flag=wx.RIGHT, border=8)
        self.results_text = wx.TextCtrl(panel, style=wx.TE_MULTILINE)
        vbox.Add(self.results_text, proportion=1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
        vbox.Add(hbox1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)

        self.progress = wx.Gauge(panel, range=100, size=(250, 25), style=wx.GA_HORIZONTAL|wx.GA_SMOOTH)
        vbox.Add(self.progress, flag=wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT|wx.TOP, border=10)

        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        st2 = wx.StaticText(panel, label="Download:")
        hbox2.Add(st2, flag=wx.RIGHT, border=8)
        self.download_text = wx.StaticText(panel, label="")
        hbox2.Add(self.download_text, flag=wx.RIGHT, border=8)
        vbox.Add(hbox2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)

        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        st3 = wx.StaticText(panel, label="Upload:")
        hbox3.Add(st3, flag=wx.RIGHT, border=8)
        self.upload_text = wx.StaticText(panel, label="")
        hbox3.Add(self.upload_text, flag=wx.RIGHT, border=8)
        vbox.Add(hbox3, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)

        self.start_button = wx.Button(panel, label="Start")
        self.cancel_button = wx.Button(panel, label="Cancel", style=wx.BU_LEFT)

        hbox4 = wx.BoxSizer(wx.HORIZONTAL)
        hbox4.Add(self.start_button, flag=wx.RIGHT, border=8)
        hbox4.Add(self.cancel_button, flag=wx.RIGHT, border=8)
        vbox.Add(hbox4, flag=wx.ALIGN_RIGHT|wx.TOP|wx.RIGHT|wx.BOTTOM, border=10)

        panel.SetSizer(vbox)

        self.start_button.Bind(wx.EVT_BUTTON, self.on_start)
        self.c = False

    def on_start(self, event):
        print("on_start called")
        self.disable_start_button()
        self.show_cancel_button()
        self.update_status_label("Testing, please wait...")
        self.set_cancelled(False)
        self.speedtest = speedtest.Speedtest()
        self.speedtest_thread = threading.Thread(target=self.run_speedtest)
        self.speedtest_thread.start()
        self.append_output_text("Speed test started.\n")
        self.set_focus_to_cancel_button()
        speak("Testing started, please wait...")    
        # Change the "Start" button to a "Cancel" button
        self.start_button.SetLabel("Cancel")
        self.start_button.Bind(wx.EVT_BUTTON, self.on_cancel)

    def disable_start_button(self):
        self.start_button.Disable()

    def on_cancel(self, event):
        self.set_cancelled(True)
        self.cancel_button.Disable()
        self.update_status_label("Test cancelled")
        self.set_progress_value(0)
        speak ("test canceled... ")
        if self.speedtest_thread.is_alive():
            self.enable_start_button()
            self.hide_cancel_button()
            self.set_focus_to_start_button()
            self.set_start_button_label("Start")

    def run_speedtest(self):
        try:
            self.speedtest.get_best_server()
            self.speedtest.download(callback=self.speedtest_callback)
            self.speedtest.upload(callback=self.speedtest_callback)
            results_dict = self.speedtest.results.dict()
            self.display_results(results_dict)
        except speedtest.NoMatchedServers as e:
            self.display_error(str(e))
            speak(str(e))
        except Exception as e:
            self.display_error(str(e))
    
    def speedtest_callback(self, speed):
        progress = int(speed / 1000000)
        self.set_progress_value(progress)
    
    def display_results(self, results_dict):
        ping = results_dict["ping"]
        download = results_dict["download"] / 1000000
        upload = results_dict["upload"] / 1000000
        ping_str = f"{ping:.2f} ms"
        download_str = f"{download:.2f} Mbps"
        upload_str = f"{upload:.2f} Mbps"
        results = f"Ping: {ping_str}    Download: {download_str}    Upload: {upload_str}"
        wx.CallAfter(self.append_results_text, results)
        speak(results)
        self.set_progress_value(100)
        self.enable_start_button()
        self.hide_cancel_button()
        self.set_focus_to_start_button()
        self.set_start_button_label("Start")

    def update_results_text(self, text):
        self.results_text.AppendText(text + '\n')
    def display_error(self, error):
        wx.CallAfter(pub.sendMessage, "SPEEDY_ERROR", message=error)

    def show_cancel_button(self):
        self.cancel_button.Show()

    def set_progress_value(self, value):
        self.progress.SetValue(value)

    def set_cancelled(self, value):
        self.c = value

    def enable_start_button(self):
        self.start_button.Enable()


    def set_focus_to_cancel_button(self):
        self.cancel_button.SetFocus()
    def set_focus_to_start_button(self):
        self.start_button.SetFocus()

    def hide_cancel_button(self):
        self.cancel_button.Hide()

    def set_start_button_label(self, label):
        self.start_button.SetLabel(label)

    def update_status_label(self, text):
        self.results_text.AppendText(f"{text}\n")
        speak(f"{text}")