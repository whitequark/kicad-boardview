import pcbnew
import os

from .pcbnew2boardview import convert_brd, convert_bvr


class Pcbnew2Boardview_BRD(pcbnew.ActionPlugin):

    def defaults(self):
        self.name = "Pcbnew to Boardview (BRD)"
        self.category = "Read PCB"
        self.description = "Generate Boardview file from KiCad PCB."

    def Run(self):
        kicad_pcb = pcbnew.GetBoard()
        with open(kicad_pcb.GetFileName().replace('.kicad_pcb', '.brd'), 'w') as brd_file:
            convert_brd(kicad_pcb, brd_file)

class Pcbnew2Boardview_BVR(pcbnew.ActionPlugin):

    def defaults(self):
        self.name = "Pcbnew to Boardview (BVR)"
        self.category = "Read PCB"
        self.description = "Generate Boardview file from KiCad PCB."

    def Run(self):
        kicad_pcb = pcbnew.GetBoard()
        with open(kicad_pcb.GetFileName().replace('.kicad_pcb', '.bvr'), 'w') as bvr_file:
            convert_bvr(kicad_pcb, bvr_file)


plugin_brd = Pcbnew2Boardview_BRD()
plugin_brd.register()

plugin_bvr = Pcbnew2Boardview_BVR()
plugin_bvr.register()