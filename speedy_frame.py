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
        self.ping_text = wx.StaticText(panel, label="")
        hbox1.Add(self.ping_text, flag=wx.RIGHT, border=8)
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
        self.cancel_button.Bind(wx.EVT_BUTTON, self.on_cancel)

        self.speedtest_thread = threading.Thread()
        self.speedtest_thread = threading.Thread()
        self.speed = speedtest.Speedtest()
        self.speed.get_best_server()
        self.c = False

    def on_start(self, event):
        self.disable_start_button()
        self.show_cancel_button()
        self.update_status_label("Testing, please wait...")
        self.ping_text.SetValue("")
        self.progress.SetValue(0)
        self.c = False
        self.speed = speedtest.Speedtest()
        self.speed.get_best_server()
        self.speedtest_thread = threading.Thread(target=self.run_speedtest)
        self.speedtest_thread.start()
        self.append_output_text("Speed test started.\n")
        self.set_focus_to_cancel_button()
        self.start_button.SetLabel("Cancel")
        self.start_button.Bind(wx.EVT_BUTTON, self.on_cancel)

    def disable_start_button(self):
        self.start_button.Disable()

    def on_cancel(self, event):
        self.c = True
        self.cancel_button.Disable()
        self.update_status_label("Test cancelled")
        self.progress.SetValue(0)
        self.enable_start_button()
        self.hide_cancel_button()
        self.set_focus_to_start_button()
        self.set_start_button_label("Start")
        self.start_button.Bind(wx.EVT_BUTTON, self.on_start)
    def run_speedtest(self):
        try:
            self.speed.get_best_server()
            self.speed.download(callback=self.speedtest_callback)
            self.speed.upload(callback=self.speedtest_callback)
            results_dict = self.speed.results.dict()
            self.display_results(results_dict)
        except speedtest.NoMatchedServers as e:
            self.display_error(str(e))
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
        self.update_status_label(f"Ping: {ping_str}    Download: {download_str}    Upload: {upload_str}")
    
    def display_error(self, error):
        wx.CallAfter(pub.sendMessage, "SPEEDY_ERROR", message=error)

    def show_cancel_button(self):
        self.cancel_button.Show()

    def update_status_label(self, text):
        self.ping_text.SetLabel(text)

    def set_progress_value(self, value):
        self.progress.SetValue(value)

    def set_cancelled(self, value):
        self.c = value

    def append_output_text(self, text):
        self.ping_text.SetLabel(self.ping_text.GetLabel() + text)


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
