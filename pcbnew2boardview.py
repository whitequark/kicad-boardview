#!/usr/bin/env python

import sys
import re
import argparse

import pcbnew


def skip_module(module, tp=False):
    if module.GetPadCount() == 0:
        return True
    refdes = module.Reference().GetText()
    if tp and not refdes.startswith("TP"):
        return True
    if not tp and refdes.startswith("TP"):
        return True
    return False


def coord(nanometers):
    milliinches = nanometers * 5 // 127000
    return milliinches


def y_coord(maxy, y, flipped):
    # Adjust y-coordinate to start from the bottom of the board and account for flipped components
    return coord(maxy - y) if not flipped else coord(y)

def natural_sort_key(s):
    is_blank = s.strip() == ''
    return (is_blank, [int(text) if text.isdigit() else text.casefold()
                       for text in re.compile('([0-9]+)').split(s)])


def convert_brd(pcb, brd):
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
                          y=y_coord(outline_maxy, point.y, False)))
    if outline.IsClosed():
        brd.write("{x} {y}\n"
                  .format(x=coord(outline_points[0].x),
                          y=y_coord(outline_maxy, outline_points[0].y, False)))
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
        flipped = module.IsFlipped()
        brd.write("{ref} {x1} {y1} {x2} {y2} {pin} {side}\n"
                  .format(ref=module.Reference().GetText(),
                          x1=coord(module_bbox.GetLeft()),
                          y1=y_coord(outline_maxy, module_bbox.GetTop(), flipped),
                          x2=coord(module_bbox.GetRight()),
                          y2=y_coord(outline_maxy, module_bbox.GetBottom(), flipped),
                          pin=pin_at,
                          side=1 + flipped))
        pin_at += module.GetPadCount()
    brd.write("\n")

    # Pins
    module_list = pcb.GetFootprints()
    pads = []
    for module in module_list:
        if not skip_module(module):
            pads_list = module.Pads()
            for pad in sorted(pads_list, key=lambda pad: natural_sort_key(pad.GetName())):
                pads.append(pad)

    brd.write("PINS: {count}\n"
              .format(count=len(pads)))
    for pad in pads:
        pad_pos = pad.GetPosition()
        flipped = pad.IsFlipped()
        brd.write("{x} {y} {net} {side}\n"
                  .format(x=coord(pad_pos.x),
                          y=y_coord(outline_maxy, pad_pos.y, flipped),
                          net=pad.GetNetCode(),
                          side=1 + flipped))
    brd.write("\n")

    # Nails
    module_list = pcb.GetFootprints()
    testpoints = []
    for module in module_list:
        if not skip_module(module, tp=True):
            pads_list = module.Pads()
            for pad in sorted(pads_list, key=lambda pad: natural_sort_key(pad.GetName())):
                testpoints.append((module, pad))

    brd.write("NAILS: {count}\n"
              .format(count=len(testpoints)))
    for module, pad in testpoints:
        pad_pos = pad.GetPosition()
        flipped = pad.IsFlipped()
        brd.write("{probe} {x} {y} {net} {side}\n"
                  .format(probe=module.GetReference()[2:],
                          x=coord(pad_pos.x),
                          y=y_coord(outline_maxy, pad_pos.y, flipped),
                          net=pad.GetNetCode(),
                          side=1 + flipped))
    brd.write("\n")


def convert_bvr(pcb, bvr):
    bvr.write("BVRAW_FORMAT_3\n")
    
    outlines = pcbnew.SHAPE_POLY_SET()
    pcb.GetBoardPolygonOutlines(outlines)
    outline = outlines.Outline(0)
    outline_points = [outline.GetPoint(n) for n in range(outline.PointCount())]
    outline_maxx = max(map(lambda p: p.x, outline_points))
    outline_maxy = max(map(lambda p: p.y, outline_points))
    
    module_list = pcb.GetFootprints()
    modules = []
    for module in module_list:
        if not skip_module(module):
            modules.append(module)

        ref = module.GetReference()
        flipped = module.IsFlipped()
        side = "B" if flipped else "T"
        mount = module.GetTypeName()
        pads_list = module.Pads()
        
        bvr.write("\n")
        bvr.write(f"PART_NAME {ref}\n")
        bvr.write(f"   PART_SIDE {side}\n")
        bvr.write("   PART_ORIGIN 0.000 0.000\n")
        bvr.write(f"   PART_MOUNT {mount}\n")
        bvr.write("\n")
        
        for pad in sorted(pads_list, key=lambda pad: natural_sort_key(pad.GetName())):
            pin_num = pad.GetNumber()
            net = pad.GetNetname()
            pad_bbox = pad.GetBoundingBox()
            pad_size = pad.GetSize()
            
            x_center = (pad_bbox.GetLeft() + pad_bbox.GetRight()) / 2
            y_center = (pad_bbox.GetTop() + pad_bbox.GetBottom()) / 2
            x = coord(x_center)
            y = y_coord(outline_maxy, y_center, flipped)
            
            if flipped:
                y = coord(outline_maxy - y_center)
                
            if pad.GetShape() == pcbnew.PAD_SHAPE_CIRCLE:
                radius = coord(pad_size.x / 1.6)
            else:
                smaller_dimension = min(pad_size.x, pad_size.y)
                radius = coord(smaller_dimension / 1.6)
            
            bvr.write(f"   PIN_ID {ref}-{pin_num}\n")
            bvr.write(f"      PIN_NUMBER {pin_num}\n")
            bvr.write(f"      PIN_NAME {pin_num}\n")
            bvr.write(f"      PIN_SIDE {side}\n")
            bvr.write(f"      PIN_ORIGIN {x} {y}\n")
            bvr.write(f"      PIN_RADIUS {radius}\n")
            bvr.write(f"      PIN_NET {net}\n")
            bvr.write("      PIN_TYPE 2\n")
            bvr.write("      PIN_COMMENT\n")
            bvr.write("   PIN_END\n")
            bvr.write("\n")
        
        bvr.write("PART_END\n")
        bvr.write("\n")
        
        first_point = outline_points[0]
        outline_pts = ""
        
    for point in outline_points:
        x = coord(point.x)
        y = y_coord(outline_maxy, point.y, False)
        outline_pts += (f"{x} {y} ")
    
    x = coord(first_point.x)
    y = y_coord(outline_maxy, first_point.y, False)
    outline_pts += (f"{x} {y}")
    
    bvr.write("OUTLINE_POINTS ")
    bvr.write(outline_pts)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "kicad_pcb_file", metavar="KICAD-PCB-FILE", type=str,
        help="input in .kicad_pcb format")
    parser.add_argument(
        "brd_file", metavar="BRD-FILE", type=argparse.FileType("w"),
        help="output in .brd format")
    parser.add_argument(
        "--bvr_file", metavar="BVR-FILE", type=argparse.FileType("w"),
        help="output in .bvr format")

    args = parser.parse_args()
    board = pcbnew.LoadBoard(args.kicad_pcb_file)
    convert_brd(board, args.brd_file)
    if args.bvr_file:
        convert_bvr(board, bvr_file)


if __name__ == "__main__":
    main()