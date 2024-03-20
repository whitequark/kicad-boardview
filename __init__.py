import pcbnew
import os

from .pcbnew2boardview import convert_brd, convert_obdata


class Pcbnew2Boardview(pcbnew.ActionPlugin):

    def defaults(self):
        self.name = "Pcbnew to Boardview"
        self.category = "Read PCB"
        self.description = "Generate Boardview file from KiCad PCB."

    def Run(self):
        kicad_pcb = pcbnew.GetBoard()
        with open(kicad_pcb.GetFileName().replace('.kicad_pcb', '.brd'), 'w') as brd_file:
            convert_brd(kicad_pcb, brd_file)
            
class Pcbnew2OpenBoardData(pcbnew.ActionPlugin):
    
    def defaults(self):
        self.name = "Pcbnew to OpenBoardData"
        self.category = "Export Board Data"
        self.description = "Generate OpenBoardData file from KiCad PCB."

    def Run(self):
        kicad_pcb = pcbnew.GetBoard()
        with open(kicad_pcb.GetFileName().replace('.kicad_pcb', '.obdata'), 'w') as obdata_file:
            convert_obdata(kicad_pcb, obdata_file)


plugin_brd = Pcbnew2Boardview()
plugin_brd.register()

plugin_obdata = Pcbnew2OpenBoardData()
plugin_obdata.register()