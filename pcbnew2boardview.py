#!/usr/bin/env python

import sys
import re
import argparse

import pcbnew


def skip_module(module, tp=False):
    refdes = module.Reference()
    if refdes == "REF**":
        return True
    if tp and not refdes.GetText().startswith("TP"):
        return True
    if not tp and refdes.GetText().startswith("TP"):
        return True
    return False


def coord(nanometers):
    milliinches = nanometers * 5 // 127000
    return milliinches


def y_coord(obj, maxy, y):
    if obj.IsFlipped():
        return coord(maxy - y)
    else:
        return coord(y)

def pad_sort_key(name):
    if re.match(r"^\d+$", name):
        return (0, int(name))
    else:
        return (1, name)


def convert(pcb, brd):
    # Board outline
    outlines = pcbnew.SHAPE_POLY_SET()
    pcb.GetBoardPolygonOutlines(outlines)
    outline = outlines.Outline(0)
    outline_points = [outline.GetPoint(n) for n in range(outline.PointCount())]
    outline_maxx = max(map(lambda p: p.x, outline_points))
    outline_maxy = max(map(lambda p: p.y, outline_points))

    brd.write("0\n") # unknown

    brd.write("BRDOUT: {count} {width} {height}\n"
              .format(count =len(outline_points) + outline.IsClosed(),
                      width =coord(outline_maxx),
                      height=coord(outline_maxy)))
    for point in outline_points:
        brd.write("{x} {y}\n"
                  .format(x=coord(point.x),
                          y=coord(point.y)))
    if outline.IsClosed():
        brd.write("{x} {y}\n"
                  .format(x=coord(outline_points[0].x),
                          y=coord(outline_points[0].y)))
    brd.write("\n")

    # Nets
    net_info = pcb.GetNetInfo()
    net_items = [net_info.GetNetItem(n) for n in range(1, net_info.GetNetCount())]

    brd.write("NETS: {count}\n"
              .format(count=len(net_items)))
    for net_item in net_items:
        brd.write("{code} {name}\n"
                  .format(code=net_item.GetNetCode(),
                          name=net_item.GetNetname()))
    brd.write("\n")

    # Parts
    module_list = pcb.GetFootprints()
    modules = []
    for module in module_list:
        if not skip_module(module):
            modules.append(module)

    brd.write("PARTS: {count}\n"
              .format(count=len(modules)))
    pin_at = 0
    for module in modules:
        module_bbox = module.GetBoundingBox()
        brd.write("{ref} {x1} {y1} {x2} {y2} {pin} {side}\n"
                  .format(ref=module.Reference().GetText(),
                          x1 =coord(module_bbox.GetLeft()),
                          y1 =y_coord(module, outline_maxy, module_bbox.GetTop()),
                          x2 =coord(module_bbox.GetRight()),
                          y2 =y_coord(module, outline_maxy, module_bbox.GetBottom()),
                          pin=pin_at,
                          side=1 + module.IsFlipped()))
        pin_at += module.GetPadCount()
    brd.write("\n")

    # Pins
    module_list = pcb.GetFootprints()
    pads = []
    for module in module_list:
        if not skip_module(module):
            pads_list = module.Pads()
            for pad in sorted(pads_list, key=lambda pad: pad_sort_key(pad.GetName())):
                pads.append(pad)

    brd.write("PINS: {count}\n"
              .format(count=len(pads)))
    for pad in pads:
        pad_pos = pad.GetPosition()
        brd.write("{x} {y} {net} {side}\n"
                  .format(x=coord(pad_pos.x),
                          y=y_coord(pad, outline_maxy, pad_pos.y),
                          net=pad.GetNetCode(),
                          side=1 + pad.IsFlipped()))
    brd.write("\n")

    # Nails
    module_list = pcb.GetFootprints()
    testpoints = []
    for module in module_list:
        if not skip_module(module, tp=True):
            pads_list = module.Pads()
            for pad in sorted(pads_list, key=lambda pad: pad_sort_key(pad.GetName())):
                testpoints.append((module, pad))

    brd.write("NAILS: {count}\n"
              .format(count=len(testpoints)))
    for module, pad in testpoints:
        pad_pos = pad.GetPosition()
        brd.write("{probe} {x} {y} {net} {side}\n"
                  .format(probe=module.GetReference()[2:],
                          x=coord(pad_pos.x),
                          y=y_coord(pad, outline_maxy, pad_pos.y),
                          net=pad.GetNetCode(),
                          side=1 + pad.IsFlipped()))
    brd.write("\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "kicad_pcb_file", metavar="KICAD-PCB-FILE", type=str,
        help="input in .kicad_pcb format")
    parser.add_argument(
        "brd_file", metavar="BRD-FILE", type=argparse.FileType("wt"),
        help="output in .brd format")

    args = parser.parse_args()
    convert(pcbnew.LoadBoard(args.kicad_pcb_file), args.brd_file)


if __name__ == "__main__":
    main()
