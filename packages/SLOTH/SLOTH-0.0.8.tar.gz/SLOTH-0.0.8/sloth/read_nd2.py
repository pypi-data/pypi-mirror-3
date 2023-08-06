# -*- coding: utf-8 -*-
#  This file is part of SLOTH - stick/like object tracking in high-resolution.
#    Copyright (C) 2012 Monika Kauer
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#@authors: M.Kauer, B.Kauer
import struct, array, StringIO
class Nd2File:
    "Read Nikon ND2 format as produced by NIS-Elements AR 4.00.03 (Build 775)"
    def __init__(self, f):
        self.f = f
        self.chunks   = self.read_chunkmap()
        self.meta = {}
        for name in filter(lambda x: x.endswith("LV!") or "LV|" in x, self.chunks.keys()):
            self.meta.update(self.read_lv_encoding(self.read_chunk(self.chunks[name]), 1))
        self.attr = self.meta["SLxImageAttributes"]

    def read_chunk(self, chunk):
        self.f.seek(chunk[0])
        h = struct.unpack("IIQ", self.f.read(16))
        assert h[0] == 0xabeceda, "invalid magic %x"%h[0]
        self.f.seek(chunk[0]+16+h[1])
        return self.f.read(h[2])

    def read_chunkmap(self):
        "read the map of the chunks at the end of the file"
        self.f.seek(-40, 2)
        mapptr=struct.unpack("32sQ", self.f.read(40))
        assert mapptr[0]=="ND2 CHUNK MAP SIGNATURE 0000001!"
        data = self.read_chunk(mapptr[1:])
        pos = 0
        res = {}
        while True:
            p =  data.index("!",pos)+1
            res[data[pos:p]] = struct.unpack("QQ", data[p : p+16])
            # abort if we found the magic end
            if data[pos:p] == mapptr[0]:
                break
            pos = p + 16
        return res

    def read_coordinates(self):
        """read the microscope coordinates and temperatures
        Missing: get chunknames and types from xml metadata"""
        res = {}
        fmt_double = ["X","Y", "Z", "Z1", "Z2", "AcqTimesCache", "CameraTemp1", "CameraTemp2"]
        fmt_int    = ["AcqFramesCache", "PFS_OFFSET", "PFS_STATUS"]
        for postfix in fmt_double+fmt_int:
            name = "CustomData|%s!"%postfix
            if name in self.chunks:
                st = self.read_chunk(self.chunks[name])
                res[postfix] = array.array(postfix in fmt_int and "I" or "d", st)
        return res

    def read_lv_encoding(self, data, count):
        data = StringIO.StringIO(data)
        res = {}
        for c in range(count):
            lastpos = data.tell()
            hdr = data.read(2)
            if not hdr:
                break
            typ = ord(hdr[0])
            name = data.read(2*ord(hdr[1]))
            name = name.decode("utf16")[:-1].encode("utf8")
            if typ == 1:
                value, = struct.unpack("B", data.read(1))
            elif typ in [2, 3]:
                value, = struct.unpack("I", data.read(4))
            elif typ == 5:
                value, = struct.unpack("Q", data.read(8))
            elif typ == 6:
                value, = struct.unpack("d", data.read(8))
            elif typ == 8:
                value = data.read(2)
                while value[-2:] != "\x00\x00":
                    value += data.read(2)
                value = value.decode("utf16")[:-1].encode("utf8")
            elif typ == 9:
                cnt, = struct.unpack("Q", data.read(8))
                value = array.array("B", data.read(cnt))
            elif typ == 11:
                newcount,length = struct.unpack("<IQ", data.read(12))
                length -= data.tell()-lastpos
                value = self.read_lv_encoding(data.read(length), newcount)
                # XXX do not know for what these offsets? are
                unknown = array.array("I", data.read(newcount*8))
            else:
                assert 0, "%s hdr %x:%x unknown"%(name, ord(hdr[0]),  ord(hdr[1]))
            if not name in res:
                res[name] = value
            else:
                if type(res[name]) != type([]):
                    res[name] = [res[name]]
                res[name].append(value)
        x = data.read()
        assert not x, "skip %d %s"%(len(x), repr(x[:30]))
        return res

    def get_image(self, nr):
        assert nr >= 0 and nr < self.attr["uiSequenceCount"]
        assert self.attr["ePixelType"] == 1

        d = self.read_chunk(self.chunks["ImageDataSeq|%d!"%nr])
        acqtime = struct.unpack("d", d[:8])[0]
        res = [acqtime]
        for i in range(self.attr["uiComp"]):
            a = array.array("H", d)
            res.append(a[4+i::self.attr["uiComp"]])
        return res

    def get_ppm(self, nr, layer):
        x = self.get_image(nr)
        layer = x[layer+1]
        m = max(layer)
        layer.byteswap()
        return "P5\n%d %d\n%d\n"%(self.attr["uiWidth"], self.attr["uiHeight"], m) + layer.tostring()

class SeedDetection:
    def __init__(self, **args):
        self.args = args

    def debug(self, *x):
        print >>sys.stderr, " ".join(map(str, x))

    def draw_line(self, image, width, color, x1, y1, x2, y2):
        "simple bresenham"
        deltax, deltay =  abs(x2 - x1), -abs(y2 - y1)
        err = deltax + deltay
        while True:
            image[y1*width+x1] = color
            if x1 == x2 and y1 == y2:
                break
            e = 2*err
            if e > deltay:
                err += deltay
                x1 += x1 < x2 and 1 or -1
            if e < deltax:
                err += deltax
                y1 += y1 < y2 and 1 or -1

    def new_object(self, objects, hints, y, xmin, xmax):
        "add a new horizontal line segment as new object and merge with old objects"
        v = (y, xmin, xmax)
        objectnr = None
        for nr in hints.get(y-1, []):
            items = objects.get(nr, [])
            for i in range(len(items)-1, -1, -1):
                if items[i][0] < (y - 1):  break
                if items[i][0] == y:       continue
                assert items[i][0] == y -1
                if max(xmin, items[i][1]) <= min(xmax, items[i][2]):
                    if not objectnr:
                        objectnr = nr
                    else:
                        objects[objectnr] = list(set(objects[objectnr]).union(items))
                        objects[objectnr].sort()
                        del objects[nr]
                    break
        if objectnr:
            objects[objectnr].append(v)
        else:
            objectnr = (y<<16)+xmin
            assert objectnr not in objects
            objects[objectnr] = [v]
        hints.setdefault(y, set())
        hints[y].add(objectnr)

    def detect_objects(self, image, width, height):
        "detect objects line by line by checking for a certain limit"
        use_green = self.args["use_green"]
        parameter = self.args["parameter"]
        maximum   = max(image[1]) + (use_green and max(image[2]) or 0)
        minimum   = min(image[1]) + (use_green and min(image[2]) or 0)
        objects   = {}
        hints     = {}
        output    = self.args["output_ppm"] and use_green
        layer     = image[1]

        prev = False
        diff = (maximum-minimum) / parameter
        for i in range(height*width):
            value = image[1][i]
            if use_green:
                value += image[2][i]
            v = (value-minimum) > diff
            if v != prev:
                if not v:
                    end = i - 1
                    y = end/width
                    while start/width != y:
                        self.new_object(objects, hints, start/width, start % width, width-1)
                        start += width - (start % width)
                    self.new_object(objects, hints, y, start % width, end%width)
                prev = v
                start = i
            if output:
                layer[i] = value # v and max(maximum/2,value) or value
        return layer, objects

    def filter_objects(self, objects, width, height):
        "filter objects that are to short, to thick or out of bounds"
        accounting = {"count": 0, "length": 0, "bounds":0, "thick": 0}
        res = []
        for k in objects:
            items = objects[k]
            pymin = (items[ 0][1],items[ 0][0])
            pymax = (items[-1][1],items[-1][0])
            pxmin = pymin
            pxmax = pymin
            for i in items:
                if i[2] > pxmax[0]: pxmax = (i[2],i[0])
                if i[1] < pxmin[0]: pxmin = (i[1],i[0])
            vx = (pxmax[0] - pxmin[0]+1)**2
            vy = (pymax[1] - pymin[1]+1)**2
            l1 = (pxmin[0]-pymin[0])**2+(pxmin[1]-pymin[1])**2
            l2 = (pymin[0]-pxmax[0])**2+(pymin[1]-pxmax[1])**2
            l3 = (pxmax[0]-pymax[0])**2+(pxmax[1]-pymax[1])**2
            l4 = (pymax[0]-pxmin[0])**2+(pymax[1]-pxmin[1])**2
            thickness = min(max(l1, l3), max(l2,l4), vx, vy)**0.5
            length = (vx+vy)**0.5
            # guarantee a minimum length
            if length < self.args["minlength"]:
                accounting["length"]+=1
                #self.debug("(%3d %3d)"%pymin,"(%3d %3d)"%pymax, "%6.2f"%length, "skip length")
                reason = 1
            # make sure it is not outside the picture
            elif not pxmin[0] or pxmax[0] == width-1 or not pymin[1] or pymax[1] == height-1:
                accounting["bounds"]+=1
                #self.debug("(%3d %3d)"%pxmin,"(%3d %3d)"%pxmax, "(%3d %3d)"%pymin,"(%3d %3d)"%pymax, "skip bounds")
                reason = 2
            # and that it is not to thick
            elif thickness > self.args["maxthickness"]:
                accounting["thick"]+=1
                #self.debug("(%3d %3d)"%pxmin,"(%3d %3d)"%pxmax, "(%3d %3d)"%pymin,"(%3d %3d)"%pymax, "%6.2f"%thickness, "skip thickness")
                reason = 3
            else:
                self.debug("(%3d %3d)"%pxmin,"(%3d %3d)"%pxmax, "(%3d %3d)"%pymin,"(%3d %3d)"%pymax, "len", "%6.2f"%length, "thick", "%6.2f"%thickness, "ok")
                accounting["count"]+=1
                reason = 0
            res.append((pxmin, pxmax, pymin, pymax, items, reason))
        return accounting, res

    def detect(self, image, width, height, nr):
        self.debug("start picture", nr, self.args)
        layer,objects = self.detect_objects(image, width, height)
        accounting,objects = self.filter_objects(objects, width, height)
        self.debug("end picture", nr, accounting)

        if not self.args["output_ppm"]: return
        m = max(max(layer), 0x100)
        # draw the lines into the picture
        for pxmin,pxmax, pymin, pymax, items, reason in objects:
            for y,xmin,xmax in items:
                self.draw_line(layer, width, [0, m, m/2, m/2][reason], xmin, y, xmax, y)
            # diagonals
            self.draw_line(layer, width, m, pxmin[0], pxmin[1], pxmax[0], pxmax[1])
            self.draw_line(layer, width, m, pymin[0], pymin[1], pymax[0], pymax[1])
            # boundary
            #self.draw_line(layer, width, m, pxmin[0], pxmin[1], pymin[0], pymin[1])
            #self.draw_line(layer, width, m, pymin[0], pymin[1], pxmax[0], pxmax[1])
            #self.draw_line(layer, width, m, pxmax[0], pxmax[1], pymax[0], pymax[1])
            #self.draw_line(layer, width, m, pymax[0], pymax[1], pxmin[0], pxmin[1])
        # output the PPM file
        layer.byteswap()
        sys.stdout.write("P5\n%d %d\n%d\n"%(width, height, m) + layer.tostring())


if __name__ == "__main__":
    import sys, pprint
    filename = filter(lambda x: not x.startswith("-"), sys.argv[1:])[0]
    nd = Nd2File(open(filename))

    if "-m" in sys.argv:
        pprint.pprint(nd.meta)
    elif "-c" in sys.argv:
        keys = nd.chunks.keys()
        keys.sort()
        for k in keys:
            print k
    elif "-x" in sys.argv:
        import xml.dom.minidom as xml
        for name in filter(lambda x:x.startswith("CustomDataVar|"), nd.chunks):
            x = xml.parseString(nd.read_chunk(nd.chunks[name]))
            print x.toprettyxml().encode("utf8"),
    elif "-t" in sys.argv:
        for n in nd.meta["SLxImageTextInfo"]:
            if nd.meta["SLxImageTextInfo"][n]:
                print nd.meta["SLxImageTextInfo"][n]
    elif "-a0" in sys.argv:
        for i in range(nd.attr["uiSequenceCount"]):
            sys.stdout.write(nd.get_ppm(i, 0))
    elif "-a1" in sys.argv:
        for i in range(nd.attr["uiSequenceCount"]):
            sys.stdout.write(nd.get_ppm(i, 1))        
    elif "-p" in sys.argv:
        for i in range(nd.attr["uiComp"]):
            sys.stdout.write(nd.get_ppm(12, i))
    elif "-z" in sys.argv:
        detect = SeedDetection(parameter=4.25, minlength=15, maxthickness=15, use_green=False, output_ppm=True)
        detect.detect(nd.get_image(0), nd.attr["uiWidth"], nd.attr["uiHeight"], 0)
        detect.args["use_green"] = True
        for i in range(min(1000, nd.attr["uiSequenceCount"])):
            detect.detect(nd.get_image(i), nd.attr["uiWidth"], nd.attr["uiHeight"], i)
    else:
        print "Usage %s -[cmxtap] FILE"%sys.argv[0]

