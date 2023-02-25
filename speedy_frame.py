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

        self.speedtest_thread = None
        self.speed = None
        self.c = False

    def on_start(self, event):
        self.disable_start_button()
        self.show_cancel_button()
        self.update_status_label("Testing, please wait...")
        self.output.SetValue("")
        self.progress.SetValue(0)
        self.c = False
        self.speed = speedtest.Speedtest()
        self.speed.get_best_server()
        self.speedtest_thread = threading.Thread(target=self.run_speedtest)
        self.speedtest_thread.start()
        self.append_output_text("Speed test started.\n")
        self.set_focus_to_cancel_button()
        self.start.SetLabel("Cancel")
        self.start.Bind(wx.EVT_BUTTON, self.on_cancel)

    def on_cancel(self, event):
        self.c = True
        self.cancel.Disable()
        self.status.SetLabel("Test cancelled")
        self.progress.SetValue(0)
        self.start.Enable()
        self.cancel.Hide()
        self.append_output_text("Speed test cancelled.\n")
        self.start.SetFocus()
        self.start.SetLabel("Start")
        self.start.Bind(wx.EVT_BUTTON, self.on_start)

    def run_speedtest(self):
        try:
            self.speed.get_best_server()
            self.update_status_label("Testing download speed...")
            self.append_output_text("Testing download speed...\n")
            dl_speed = self.speed.download(threads=None, callback=lambda c, t: self.progress.SetValue(int(c / t * 100)))
            if self.c:
                return
            self.update_status_label("Testing upload speed...")
            self.append_output_text("Testing upload speed...\n")
            ul_speed = self.speed.upload(threads=None, callback=lambda c, t: self.progress.SetValue(int(c / t * 100)))
            if self.c:
                return
            self.enable_start_button()
            self.hide_cancel_button()
            self.set_progress_value(100)
            out_text = f"Download speed: {dl_speed / 1_000_000:.2f} Mbps\nUpload speed: {ul_speed / 1_000_000:.2f} Mbps"
            self.update_status_label(out_text)
            self.append_output_text(out_text + "\n")
            self.append_output_text("Speed test completed.\n")
            self.set_focus_to_start_button()
            self.set_start_button_label("Start")
            self.start.Bind(wx.EVT_BUTTON, self.on_start)

            # Publish the SpeedtestCompletedEvent to notify other parts of the application that the speed test is completed
            pub.sendMessage("speedtest_completed", ping_speed=0, download_speed=dl_speed, upload_speed=ul_speed)

        except Exception as e:
            self.enable_start_button()
            self.hide_cancel_button()
            self.set_progress_value(0)
            self.update_status_label("An error occurred during the speed test. Please try again later.")
            wx.LogError(str(e))

    def set_cancelled(self, value):
        self.c = value

    def hide_cancel_button(self):
        self.cancel.Hide()

    def set_focus_to_start_button(self):
        self.start.SetFocus()

    def set_focus_to_cancel_button(self):
        self.cancel.SetFocus()

    def set_start_button_label(self, label):
        self.start.SetLabel(label)

    def set_cancel_button_label(self, label):
        self.cancel.SetLabel(label)

    def enable_start_button(self):
        self.start.Enable()

    def disable_start_button(self):
        self.start_button.Disable()

    def show_cancel_button(self):
        self.cancel.Show()

    def append_output_text(self, text):
        self.output.AppendText(text)

    def update_status_label(self, text):
        self.status.SetLabel(text)

    def set_progress_value(self, value):
        self.progress.SetValue(value)

