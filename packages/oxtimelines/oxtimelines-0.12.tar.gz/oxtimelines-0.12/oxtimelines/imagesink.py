# -*- coding: utf-8 -*-
# vi:si:et:sw=4:sts=4:ts=4
# GPL 2008
import gobject

import pygst
pygst.require("0.10")
import gst

import Image


class ImageSink(gst.BaseSink):
    #def log(self, msg):
    #    print msg

    __gsignals__ = {
        "frame" : (gobject.SIGNAL_RUN_LAST,
                   gobject.TYPE_NONE,
                   ( gobject.TYPE_PYOBJECT, gobject.TYPE_UINT64 ))
        }

    __gsttemplates__ = (
        gst.PadTemplate ("sink",
                         gst.PAD_SINK,
                         gst.PAD_ALWAYS,
                         gst.Caps("video/x-raw-rgb,"
                                  "bpp = (int) 24, depth = (int) 24,"
                                  "endianness = (int) BIG_ENDIAN,"
                                  "red_mask = (int) 0x00FF0000, "
                                  "green_mask = (int) 0x0000FF00, "
                                  "blue_mask = (int) 0x000000FF, "
                                  "width = (int) [ 1, max ], "
                                  "height = (int) [ 1, max ], "
                                  "framerate = (fraction) [ 0, max ]"))
        )

    def __init__(self, callback):
        gst.BaseSink.__init__(self)
        self.callback = callback
        self.width = 1
        self.height = 1
        self.set_sync(False)

    def do_set_caps(self, caps):
        self.log("caps %s" % caps.to_string())
        self.log("padcaps %s" % self.get_pad("sink").get_caps().to_string())
        self.width = caps[0]["width"]
        self.height = caps[0]["height"]
        self.framerate = caps[0]["framerate"]

        if not caps[0].get_name() == "video/x-raw-rgb":
            return False
        return True

    def do_render(self, buf):
        '''
        self.log("buffer %s %d" % (
            gst.TIME_ARGS(buf.timestamp), len(buf.data)
        ))
        '''
        frame_image = Image.fromstring('RGB', (self.width, self.height), buf.data)
        # self.emit('frame', frame, buf.timestamp)
        self.callback(frame_image, buf.timestamp)
        return gst.FLOW_OK

    def do_preroll(self, buf):
        return self.do_render(buf)

gobject.type_register(ImageSink)

