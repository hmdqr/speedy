import wx
import threading
import speedtest
from speedy_frame import *


def on_start(event):
    frame = event.GetEventObject().GetParent()
    frame.disable_start_button()
    frame.show_cancel_button()
    frame.update_status_label("testing, please wait...")
    frame.output.SetValue("")
    frame.progress.SetValue(0)
    frame.set_cancelled(False)
    frame.speed = speedtest.Speedtest()
    frame.thread = threading.Thread(target=run_speedtest, args=(frame,))
    frame.thread.start()
    frame.append_output_text("Speed test started.\n")


def on_cancel(event):
    frame = event.GetEventObject().GetParent()
    frame.set_cancelled(True)
    frame.cancel.Disable()
    frame.update_status_label("test cancelled")
    frame.progress.SetValue(0)
    frame.enable_start_button()
    frame.hide_cancel_button()
    frame.append_output_text("Speed test cancelled.\n")


def run_speedtest(frame):
    try:
        # Find best server and test download speed
        frame.speed.get_best_server()
        frame.update_status_label("testing download speed...")
        frame.append_output_text("Testing download speed...\n")
        download_speed = frame.speed.download(threads=None, callback=frame.update_progress_bar)

        # Check if test was cancelled
        if frame.is_cancelled():
            return

        # Test upload speed
        frame.update_status_label("testing upload speed...")
        frame.append_output_text("Testing upload speed...\n")
        upload_speed = frame.speed.upload(threads=None, callback=frame.update_progress_bar)

        # Check if test was cancelled
        if frame.is_cancelled():
            return

        # Enable start button, hide cancel button, and set progress bar to 100%
        frame.enable_start_button()
        frame.hide_cancel_button()
        frame.progress.SetValue(100)

        # Display speed test results in status label and output
        output_text = f"Download speed: {download_speed / 1_000_000:.2f} Mbps\nUpload speed: {upload_speed / 1_000_000:.2f} Mbps"
        frame.update_status_label(output_text)
        frame.append_output_text(output_text + "\n")
        frame.append_output_text("Speed test completed.\n")
    except Exception as e:
        frame.enable_start_button()
        frame.hide_cancel_button()
        frame.progress.SetValue(0)
        frame.update_status_label("An error occurred during the speed test. Please try again later.")
        frame.append_output_text("An error occurred during the speed test: " + str(e) + "\n")
