#!/usr/bin/env python
import sys, os, biobricks as bb

if len(sys.argv) == 1:
   print("Usage: bbrick <command> <args>")
   sys.exit(0)

cmd = sys.argv[1]


if cmd == "init":
   bb.bb_init()
elif cmd == "import":
   bb.bb_import(sys.argv[2])
else:
   print("Unknown command: " + cmd)
    
