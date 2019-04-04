##
from looper import Looper
import threading
from interface import GetchInterface

cname = 'getch'

gi = GetchInterface(output_port_name=cname)
looper = Looper(controller_name=cname)

threading.Thread(target=looper.run).start()
gi.run()

##
