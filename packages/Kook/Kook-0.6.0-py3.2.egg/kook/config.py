# -*- coding: utf-8 -*-

###
### $Release: 0.6.0 $
### copyright(c) 2008-2011 kuwata-lab.com all rights reserved.
### MIT License
###

import sys as _sys
import kook.utils as _utils

quiet            = False
forced           = False
noexec           = False
debug_level      = 0       #  1: debug, 2: trace
command_prompt   = '$ '
message_prompt   = '### '
warning_prompt   = '*** WARNING: '
debug_prompt     = '*** debug: '
compare_contents = True
cmdopt_parser_class = _utils.CommandOptionParser
properties_filename = 'Properties.py'
cookbook_filename   = 'Kookbook.py'
stdout           = _sys.stdout
stderr           = _sys.stderr
