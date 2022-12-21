#!/usr/bin/env python
import sys, os, biobricks as bb

# TODO kiln install seems broken
if len(sys.argv) == 1:
   print("""usage: kiln <command> <args>
   
   kiln init\tinitialize a .bb directory for importing data dependencies
   kiln import\timport a data dependency into the .bb directory
   kiln install\tinstall a data dependency into $BBLIB\n""")
   sys.exit(0)

cmd = sys.argv[1]


if cmd == "init":
   bb.bb_init()
elif cmd == "import":
   bb.bb_import(sys.argv[2])
elif cmd == "install":
   bb.pull(sys.argv[2])
else:
   print("Unknown command: " + cmd)
    
