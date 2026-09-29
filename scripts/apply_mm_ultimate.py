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

include_block = '''\n#ifdef USERMOD_WLED_ULTIMATE\n#include "../usermods/WLED_Ultimate/usermod_wled_ultimate.h"\n#endif\n'''
register_block = '''\n#ifdef USERMOD_WLED_ULTIMATE\n  usermods.add(new WLEDUltimateUsermod("WLED Ultimate", true));\n#endif\n'''

if "usermod_wled_ultimate.h" not in text:
    marker = '#include "wled.h"\n'
    if marker not in text:
        raise SystemExit("unable to locate wled.h include marker")
    text = text.replace(marker, marker + include_block, 1)

if "new WLEDUltimateUsermod" not in text:
    marker = "void registerUsermods()\n{\n"
    if marker not in text:
        raise SystemExit("unable to locate registerUsermods() marker")
    text = text.replace(marker, marker + register_block, 1)

usermods_list.write_text(text, encoding="utf-8")
print("WLED Ultimate MM usermod registered")
