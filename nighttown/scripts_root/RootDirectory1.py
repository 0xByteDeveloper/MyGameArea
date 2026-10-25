import serverinfo

import dbg
# CH ile baþlayan ve sayý içeren deðiþkenleri filtreleyerek bul
channel_ports = {key: value for key, value in vars(serverinfo).items() if key.startswith("CH_") and isinstance(value, int)}

dbg.LogBox(str(len(serverinfo.SERVER01_CHANNEL_DICT)))
for ch_name, port in sorted(channel_ports.items()):
    dbg.LogBox(str(str(ch_name) + " : " + str(port)))
