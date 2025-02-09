import pcbnew
import os

from .pcbnew2boardview import convert_brd, convert_bvr, convert_obdata


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

class Pcbnew2OpenBoardData(pcbnew.ActionPlugin):
    
    def defaults(self):
        self.name = "Pcbnew to OpenBoardData"
        self.category = "Export Board Data"
        self.description = "Generate OpenBoardData file from KiCad PCB."

    def Run(self):
        kicad_pcb = pcbnew.GetBoard()
        with open(kicad_pcb.GetFileName().replace('.kicad_pcb', '.obdata'), 'w') as obdata_file:
            convert_obdata(kicad_pcb, obdata_file)


plugin_brd = Pcbnew2Boardview_BRD()
plugin_brd.register()

plugin_bvr = Pcbnew2Boardview_BVR()
plugin_bvr.register()

plugin_obdata = Pcbnew2OpenBoardData()
plugin_obdata.register()