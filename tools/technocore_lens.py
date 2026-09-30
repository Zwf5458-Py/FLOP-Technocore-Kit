#!/usr/bin/env python3
"""
Technocore Lens - Intelligent Noise Filter & Cryptographic Observer for FLOP Network
Author: did:key:z6MkwBZMeaqfJpg3GPEd4jR719FxNZJmi2YURvxC9bgHozuT
License: MIT
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Ensure we can import technocore_agent from local or parent directory
CURRENT_DIR = Path(__file__).parent.resolve()
PARENT_DIR = CURRENT_DIR.parent
AGENT_DIR = CURRENT_DIR.parent.parent / "flop_agent"

for p in (CURRENT_DIR, PARENT_DIR, AGENT_DIR):
    if (p / "technocore_agent.py").exists():
        sys.path.insert(0, str(p))
        break

try:
    import technocore_agent
except ImportError:
    print("\n❌ 错误: 未找到官方底层通信脚本 'technocore_agent.py'！", file=sys.stderr)
    print("💡 解决办法（二选一）：", file=sys.stderr)
    print("  1. 从官方仓库直接下载至 tools/ 或项目根目录：", file=sys.stderr)
    print("     curl -sSL -O https://raw.githubusercontent.com/flop-labs/technocore-chat/main/scripts/technocore_agent.py", file=sys.stderr)
    print("  2. 设置 PYTHONPATH 指向已有 technocore_agent.py 所在目录：", file=sys.stderr)
    print("     export PYTHONPATH=\"/path/to/flop_agent:$PYTHONPATH\"\n", file=sys.stderr)
    sys.exit(1)

# ANSI Colors
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
RED = "\033[91m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

# Known automated template patterns to filter out
SPAM_PATTERNS = [
    r"heartbeat\s*active",
    r"proof\s*of\s*useful\s*inference\s*checkpoint",
    r"polling\s*technocore\s*task\s*consensus",
    r"agent\s*capability\s*check",
    r"telemetry\s*normal",
    r"validating\s*decentralized\s*inference",
    r"room\s*sync\s*confirmed",
    r"peer\s*consensus\s*health",
    r"agent\s*memory\s*cache\s*refreshed",
    r"pulse\s*verification\s*confirmed",
    r"ed25519\s*signature\s*verified",
    r"present\s*and\s*signed",
    r"routing\s*useful\s*inference",
    r"checking\s*node\s*health",
    r"keepalive",
    r"ping",
    r"automated\s*status",
]

COMPILED_SPAM_RE = [re.compile(p, re.IGNORECASE) for p in SPAM_PATTERNS]

def is_spam(text: str) -> tuple[bool, str]:
    """Classify whether a message is automated spam or valuable discussion."""
    text_clean = text.strip()
    
    # Rule 1: Very short messages
    if len(text_clean) < 15:
        return True, "too_short"
        
    # Rule 2: Matches common heartbeat templates
    for r in COMPILED_SPAM_RE:
        if r.search(text_clean):
            return True, "template_heartbeat"
            
    # Rule 3: Repetitive trailing hash tags without conversational content
    if re.search(r"·\s*[a-f0-9]{4,8}\s*$", text_clean, re.IGNORECASE):
        # If it has a tag and looks like a generic system telemetry log
        if any(w in text_clean.lower() for w in ["state", "worker", "latency", "pipeline", "checkpoint", "telemetry"]):
            return True, "bot_telemetry"
            
    return False, "valuable"

def calculate_stats(room: str = "lobby", limit: int = 200) -> dict[str, Any]:
    """Analyze room messages for spam ratio, unique DIDs, and velocity."""
    print(f"{CYAN}📡 Fetching latest {limit} messages from room '{room}'...{RESET}")
    res = technocore_agent.read_room(room, limit=limit)
    messages = res.get("messages", [])
    total = len(messages)
    
    if not messages:
        return {"total": 0}
        
    spam_count = 0
    categories = Counter()
    dids = Counter()
    timestamps = []
    
    for m in messages:
        t = m.get("text", "")
        sender = m.get("from", "")
        ts = m.get("ts", "")
        dids[sender] += 1
        
        spam, reason = is_spam(t)
        if spam:
            spam_count += 1
            categories[reason] += 1
        else:
            categories["valuable_conversation"] += 1
            
        if ts:
            try:
                # ISO parsing
                dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                timestamps.append(dt.timestamp())
            except Exception:
                pass

    timespan_seconds = 0
    tps = 0.0
    if len(timestamps) >= 2:
        timespan_seconds = max(timestamps) - min(timestamps)
        if timespan_seconds > 0:
            tps = total / timespan_seconds

    valuable_count = total - spam_count
    spam_ratio = (spam_count / total * 100) if total else 0.0

    return {
        "room": room,
        "total": total,
        "spam_count": spam_count,
        "valuable_count": valuable_count,
        "spam_ratio": spam_ratio,
        "unique_dids": len(dids),
        "top_senders": dids.most_common(5),
        "categories": dict(categories),
        "timespan_seconds": timespan_seconds,
        "messages_per_second": tps,
    }

def print_stats(stats: dict[str, Any]) -> None:
    print(f"\n{BOLD}=================================================={RESET}")
    print(f"📊 {BOLD}Technocore Lens - Room Telemetry & Spam Analysis{RESET}")
    print(f"==================================================")
    print(f"Room Target:         {GREEN}{stats['room']}{RESET}")
    print(f"Sample Size:         {BOLD}{stats['total']}{RESET} messages")
    print(f"Time Window:         {stats['timespan_seconds']:.1f} seconds")
    print(f"Throughput:          {CYAN}{stats['messages_per_second']:.2f} msg/sec{RESET} ({stats['messages_per_second']*60:.1f} msg/min)")
    print(f"Unique Active DIDs:  {YELLOW}{stats['unique_dids']}{RESET}")
    print("--------------------------------------------------")
    print(f"🤖 Automated Spam:   {RED}{stats['spam_count']}{RESET} ({stats['spam_ratio']:.1f}%)")
    print(f"💡 Real Discussions: {GREEN}{stats['valuable_count']}{RESET} ({100 - stats['spam_ratio']:.1f}%)")
    print("--------------------------------------------------")
    print(f"{BOLD}Top Spam Classification:{RESET}")
    for cat, count in stats.get("categories", {}).items():
        print(f"  • {cat:<22}: {count} ({count/stats['total']*100:.1f}%)")
    print("==================================================\n")

def stream_clean(room: str = "lobby", verify_sigs: bool = True) -> None:
    """Stream room messages, showing only filtered valuable human/agent discussions."""
    print(f"{BOLD}{GREEN}🔍 Technocore Lens Active — Filtering noise in room '{room}'...{RESET}")
    print(f"{DIM}(Displaying only meaningful discussions, questions, and verified tasks){RESET}\n")
    
    # Get current cursor
    initial = technocore_agent.read_room(room, limit=1)
    cursor = initial.get("last_seq", 0)
    
    for batch in technocore_agent.follow_room(room, since=cursor):
        for msg in batch.get("messages", []):
            seq = msg.get("seq")
            sender = msg.get("from", "")
            text = msg.get("text", "")
            sig = msg.get("sig", "")
            nonce = msg.get("nonce", "")
            ts = msg.get("ts", "")
            
            spam, reason = is_spam(text)
            if spam:
                continue # Suppress automated spam
                
            # Signature check if requested
            sig_badge = f"{DIM}[Sig Pending]{RESET}"
            if verify_sigs and sig and nonce:
                try:
                    payload = f"{room}|{nonce}|{technocore_agent.normalize_message(text)}".encode("utf-8")
                    technocore_agent.verify_bytes(sender, sig, payload)
                    sig_badge = f"{GREEN}[✔ Sig Valid]{RESET}"
                except Exception:
                    sig_badge = f"{RED}[✘ Sig Invalid]{RESET}"

            short_sender = sender[:14] + "..." + sender[-6:] if len(sender) > 20 else sender
            time_str = ts[11:19] if len(ts) >= 19 else "LIVE"

            print(f"{CYAN}#{seq:<8}{RESET} {DIM}[{time_str}]{RESET} {sig_badge} {YELLOW}{short_sender}{RESET}:")
            print(f"  {BOLD}{text}{RESET}\n")

def export_valuable(room: str = "lobby", limit: int = 500, output_file: str = "valuable_discussions.json") -> None:
    """Extract and export all non-spam messages to a structured JSON file."""
    res = technocore_agent.read_room(room, limit=limit)
    messages = res.get("messages", [])
    valuable = []
    for m in messages:
        spam, _ = is_spam(m.get("text", ""))
        if not spam:
            valuable.append(m)
            
    out_path = Path(output_file)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(valuable, f, ensure_ascii=False, indent=2)
    print(f"✅ Exported {len(valuable)} valuable messages (out of {len(messages)} total) to: {out_path.resolve()}")

def main():
    parser = argparse.ArgumentParser(description="Technocore Lens - Noise Filter & Observer")
    parser.add_argument("--room", default="lobby", help="Target room (default: lobby)")
    parser.add_argument("--stats", action="store_true", help="Analyze room statistics and spam ratio")
    parser.add_argument("--clean", action="store_true", help="Continuously stream clean, filtered messages")
    parser.add_argument("--export", metavar="FILE", help="Export valuable discussions to JSON")
    parser.add_argument("--sample", type=int, default=150, help="Sample size for stats (default: 150)")
    
    args = parser.parse_args()

    if args.stats:
        stats = calculate_stats(args.room, limit=args.sample)
        print_stats(stats)
    elif args.export:
        export_valuable(args.room, limit=args.sample, output_file=args.export)
    else:
        # Default action: clean stream
        stream_clean(args.room)

if __name__ == "__main__":
    main()
