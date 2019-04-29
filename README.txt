# Gtsreamer Python Beginner's Guide
Part 1: https://habr.com/ru/post/178813/
Part 2: https://habr.com/ru/post/179167/
Part 3: https://habr.com/ru/post/204014/

# Gtsreamer Elements
https://gstreamer.freedesktop.org/documentation/plugins.html
shell: $ gst-inspect-1.0 <element name>

# Gtsreamer Python Bindings
https://lazka.github.io/pgi-docs/


### SERVER PIPELINE ###
gst-launch-1.0 -e v4l2src do-timestamp=true device=/dev/video0 ! image/jpeg, width=800, height=600 ! decodebin ! videoconvert ! x264enc dct8x8=1 tune=zerolatency ! rtph264pay pt=96 ! multiudpsink name=videoudp sync=true auto-multicast=false clients="192.168.1.123:6000" alsasrc do-timestamp=true ! audioconvert ! audio/x-raw, format=S24BE, layout=interleaved, rate=44100, channels=1 ! queue max-size-bytes=655360 max-size-time=62500000 ! rtpL24pay pt=98 ! multiudpsink name=audioudp sync=true auto-multicast=false clients="192.168.1.123:6002"

### CLIENT PIPELINE ###
gst-launch-1.0 -e udpsrc port=6000 ! queue ! application/x-rtp, media=video, payload=96, clock-rate=90000, encoding-name=H264 ! rtph264depay ! decodebin ! videoconvert ! xvimagesink udpsrc port=6002 ! queue ! application/x-rtp, media=audio, payload=98, clock-rate=44100, encoding-name=L24, channels=1 ! rtpL24depay ! audioconvert ! autoaudiosink
