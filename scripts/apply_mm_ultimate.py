#!/usr/bin/env python3
from pathlib import Path
import sys

if len(sys.argv) != 2:
    raise SystemExit("usage: apply_mm_ultimate.py <wled-source-dir>")

source = Path(sys.argv[1])
usermods_list = source / "wled00" / "usermods_list.cpp"

if not usermods_list.exists():
    raise SystemExit(f"missing {usermods_list}")

text = usermods_list.read_text(encoding="utf-8")

include_block = '''\n#ifdef USERMOD_WLED_ULTIMATE\n#include "../usermods/WLED_Ultimate/usermod_wled_ultimate.h"\n#endif\n\n'''
register_block = '''\n#ifdef USERMOD_WLED_ULTIMATE\n  usermods.add(new WLEDUltimateUsermod("WLED Ultimate", true));\n#endif\n'''

# Include Ultimate after the normal MM usermod headers. This is intentional:
# it lets the Ultimate bridge see AudioReactive's internal state when that
# usermod is compiled in, without modifying the external AudioReactive library.
if "usermod_wled_ultimate.h" not in text:
    marker = "\nvoid registerUsermods()\n"
    if marker not in text:
        raise SystemExit("unable to locate registerUsermods() include boundary")
    text = text.replace(marker, include_block + "void registerUsermods()\n", 1)

# Register Ultimate last so AudioReactive and other MM subsystem usermods have
# already loaded their persisted configuration before Ultimate applies master
# runtime switches.
if "new WLEDUltimateUsermod" not in text:
    end = text.rfind("\n}\n")
    if end < 0:
        raise SystemExit("unable to locate final registerUsermods() brace")
    text = text[:end] + register_block + text[end:]

usermods_list.write_text(text, encoding="utf-8")
print("WLED Ultimate MM usermod registered after subsystem usermods")
