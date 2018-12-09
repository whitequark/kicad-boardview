import pcbnew
import pcbnew2boardview
import os

class Pcbnew2Boardview(pcbnew.ActionPlugin):

    def defaults(self):
        self.name = "Pcbnew to Boardview"
        self.category = "Read PCB"
        self.description = "Generate Boardview file from KiCad pcb."

    def Run(self):
        kicad_pcb = pcbnew.GetBoard()
        with open(kicad_pcb.GetFileName().replace('.kicad_pcb', '.brd'), 'wt') as brd_file:
            pcbnew2boardview.convert(kicad_pcb, brd_file)


plugin = Pcbnew2Boardview()
plugin.register()
