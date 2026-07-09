#!/usr/bin/env python3
"""Push a single doc's mermaid to remote (for one-off testing). Usage: push_one.py <filename>"""
import sys, os
sys.path.insert(0, "/Users/bytedance/deer-flow/.agent_context/magic")
os.chdir("/Users/bytedance/deer-flow")
from push_remote import fetch_tail_block_id, block_replace, DESIGNS, MAPPING
import json
fn = sys.argv[1]
designs = json.load(open(DESIGNS, encoding="utf-8"))
mapping = json.load(open(MAPPING, encoding="utf-8"))
tok = next(m["token"] for m in mapping if m["file"] == fn)
d = designs[fn]
mm = d["mermaid"].strip()
bid = fetch_tail_block_id(tok)
print("resolved block_id:", bid)
if bid:
    rc, out, err = block_replace(tok, bid, mm)
    print("rc:", rc)
    print("out:", out[:800])
    if err.strip(): print("err:", err[:400])
