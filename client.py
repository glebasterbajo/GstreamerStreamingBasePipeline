import signal
import gi

gi.require_version("Gst", "1.0")
gi.require_version("Gtk", "3.0")
from gi.repository import Gst
from gi.repository import Gtk
from gi.repository import GObject


class Client:
    def __init__(self, v_port="6000", a_port="6002"):
        Gst.init("")
        GObject.threads_init()
        signal.signal(signal.SIGINT, signal.SIG_DFL)

        self.pipeline = Gst.parse_launch(
            f"udpsrc port={v_port} ! queue ! application/x-rtp, media=video, payload=96, clock-rate=90000, encoding-name=H264 ! rtph264depay ! decodebin ! videoconvert ! xvimagesink udpsrc port={a_port} ! queue ! application/x-rtp, media=audio, payload=98, clock-rate=44100, encoding-name=L24, channels=1 ! rtpL24depay ! audioconvert ! autoaudiosink"
        )
        self.bus = self.pipeline.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect("message", self.__on_message)

    def stop(self):
        self.pipeline.send_event(Gst.Event.new_eos())
        self.pipeline.set_state(Gst.State.NULL)

    def play(self):
        self.pipeline.set_state(Gst.State.PLAYING)
        Gtk.main()

    def __on_message(self, bus, message):
        if message.type == Gst.MessageType.EOS:
            self.pipeline.set_state(Gst.State.NULL)

        if message.type == Gst.MessageType.ERROR:
            print("Error Gstreamer: internal error")
            print(message.parse_error().gerror)
            print(message.parse_error().debug)
            self.stop()


if __name__ == "__main__":
    c = Client()
    c.play()
