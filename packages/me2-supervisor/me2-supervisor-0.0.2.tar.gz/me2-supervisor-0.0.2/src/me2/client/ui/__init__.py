import os
import clicmd

__CFGFNAME = "mderc"
__HIDDENNAME = "." + __CFGFNAME
__GLOBALCFGDIR = "/etc"
__HOMEDIRCFG = os.path.join(os.path.expanduser("~"), __HIDDENNAME)
__CURRENTDIRCFG1 = os.path.join(os.getcwd(), __HIDDENNAME)
__CURRENTDIRFCG2 = os.path.join(os.getcwd(), __CFGFNAME)
__GLOBALCONFIG = os.path.join(__GLOBALCFGDIR, __CFGFNAME)
_CFGFILES = [__GLOBALCONFIG, __HOMEDIRCFG, __CURRENTDIRCFG1, __CURRENTDIRFCG2]
