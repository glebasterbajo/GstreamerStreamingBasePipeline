import signal
import gi

gi.require_version("Gst", "1.0")
gi.require_version("Gtk", "3.0")
from gi.repository import Gst
from gi.repository import Gtk
from gi.repository import GObject


class Server:
    def __init__(self, file_path, ip="192.168.1.123", v_port="6000", a_port="6002"):
        Gst.init("")
        GObject.threads_init()
        signal.signal(signal.SIGINT, signal.SIG_DFL)

        self.pipeline = Gst.parse_launch(
            f"filesrc location={file_path}                                     \
                ! qtdemux name=demux                                           \
            demux.video_0                                                      \
                ! queue                                                        \
                ! decodebin                                                    \
                ! videoconvert                                                 \
                ! x264enc dct8x8=1 tune=zerolatency                            \
                ! rtph264pay pt=96                                             \
                ! multiudpsink                                                 \
                        name=videoudp sync=true auto-multicast=false           \
                        clients={ip}:{v_port}                                  \
            demux.audio_0                                                      \
                ! queue                                                        \
                ! decodebin                                                    \
                ! audioconvert                                                 \
                ! audio/x-raw, format=S24BE, layout=interleaved,               \
                        rate=44100, channels=1                                 \
                ! queue max-size-bytes=655360 max-size-time=62500000           \
                ! rtpL24pay pt=98                                              \
                ! multiudpsink                                                 \
                        name=audioudp sync=true auto-multicast=false           \
                        clients={ip}:{a_port}"
        )
        self.bus = self.pipeline.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect("message", self.__on_message)

    def play(self):
        self.pipeline.set_state(Gst.State.PLAYING)
        Gtk.main()

    def stop(self):
        self.pipeline.send_event(Gst.Event.new_eos())
        self.pipeline.set_state(Gst.State.NULL)

    def add_to_stream(self, ip, v_port, a_port):
        videoudp = self.pipeline.get_by_name("videoudp")
        audioudp = self.pipeline.get_by_name("audioudp")

        videoudp.emit("add", ip, v_port)
        audioudp.emit("add", ip, a_port)

    def remove_from_stream(self, ip, v_port, a_port):
        videoudp = self.pipeline.get_by_name("videoudp")
        audioudp = self.pipeline.get_by_name("audioudp")

        videoudp.emit("remove", ip, v_port)
        audioudp.emit("remove", ip, a_port)

    def __on_message(self, bus, message):
        if message.type == Gst.MessageType.EOS:
            self.pipeline.set_state(Gst.State.NULL)

        if message.type == Gst.MessageType.ERROR:
            print("Error Gstreamer: internal error")
            print(message.parse_error().gerror)
            print(message.parse_error().debug)
            self.stop()


if __name__ == "__main__":
    s = Server(file_path="2019_azerbaijan_grand_prix.mp4")
    s.play()
