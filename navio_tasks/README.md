

Tools that check, fix, package, etc.
- [Commands](Commands) are the wrappers around specific cli tools
- [lib_tools](lib_tools) are wrappers around tools w/o a cli interface

Things for build scripts
- [Build state](build_state.py) keeps track of when source code last changed relative to last
successful run
- [Clean](clean.py) deletes old outputs so that you don't get a mix of new and old
- [cli_commands](cli_commands.py) are mostly wrappers around subprocess (shell) calls
- [settings](settings.py) Per project variations

Features
--------
- Policies
    - code size cut offs (some tools don't make sense on tiny code bases)
    - strictness
- environment adaption
    - mac/window
    - container/not container
    - workstation/build server/cloud machine
    - VPN/Org Network vs No network vs Home network
- abstracting away the interface
    - every tool has its own way of specifying the files/folder to act on
    - environment variable input vs switches
    - cli interface vs importable python interface
