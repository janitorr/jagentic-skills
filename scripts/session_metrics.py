#!/usr/bin/env python3
"""Collect token, tool, model, and timing metrics from OpenCode sessions.

The source of truth is the local OpenCode SQLite store. This script reads
`session_v2` for model and token totals and `session_message` for tool calls.
It never prints assistant answers.

Examples:

    python3 scripts/session_metrics.py --recent 10 --leaves
    python3 scripts/session_metrics.py --recent 10 --leaves --directory /path/to/repo
    python3 scripts/session_metrics.py --parent ses_e535c7922ffeHoIwa0qC2Ym6r4
    python3 scripts/session_metrics.py ses_e529c3653ffeRKt98kQaZkiroT
    python3 scripts/session_metrics.py --parent ses_xxx --json
    python3 scripts/session_metrics.py --parent ses_xxx --csv > runs.csv

The table output includes a median summary. Use --json for the full record or
--csv for a spreadsheet.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sqlite3
import statistics
import sys
from collections import Counter
from datetime import datetime, timezone

DEFAULT_DB = os.path.expanduser("~/.local/share/opencode/opencode.db")

CSV_FIELDS = [
    "session",
    "parent",
    "title",
    "directory",
    "model",
    "provider",
    "variant",
    "created",
    "tokens_input",
    "tokens_output",
    "tokens_cache_read",
    "tokens_cache_write",
    "tokens_total",
    "tokens_billable",
    "cost",
    "wall_s",
    "tool_calls",
    "read_calls",
    "distinct_read_files",
    "skill_calls",
    "tools",
]


def parse_json_object(raw: str | None) -> dict:
    if not raw:
        return {}
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return value if isinstance(value, dict) else {}


def iso_time(milliseconds: int | None) -> str:
    if not milliseconds:
        return ""
    return datetime.fromtimestamp(milliseconds / 1000, tz=timezone.utc).strftime(
        "%Y-%m-%d %H:%M:%S"
    )


def session_metrics(connection: sqlite3.Connection, session_id: str) -> dict | None:
    row = connection.execute(
        """
        select id, parent_id, title, directory, model,
               tokens_input, tokens_output, tokens_cache_read, tokens_cache_write,
               cost, time_created, time_updated
        from session_v2 where id = ?
        """,
        (session_id,),
    ).fetchone()
    if row is None:
        return None

    (
        session,
        parent,
        title,
        directory,
        model_json,
        tokens_input,
        tokens_output,
        tokens_cache_read,
        tokens_cache_write,
        cost,
        time_created,
        time_updated,
    ) = row
    model = parse_json_object(model_json)

    tools: list[str] = []
    read_paths: list[str] = []
    skill_calls: list[str] = []
    for (data,) in connection.execute(
        "select data from session_message where session_id = ? order by seq",
        (session_id,),
    ):
        try:
            message = json.loads(data)
        except json.JSONDecodeError:
            continue
        for part in message.get("content", []):
            if part.get("type") != "tool":
                continue
            name = part.get("name")
            tools.append(name)
            tool_input = (part.get("state") or {}).get("input") or {}
            if name == "read" and tool_input.get("path"):
                read_paths.append(tool_input["path"])
            if name == "skill":
                skill_calls.append(tool_input.get("id"))

    tokens_total = (
        tokens_input + tokens_output + tokens_cache_read + tokens_cache_write
    )
    return {
        "session": session,
        "parent": parent or "",
        "title": title or "",
        "directory": directory or "",
        "model": model.get("id", ""),
        "provider": model.get("providerID", ""),
        "variant": model.get("variant", "default"),
        "created": iso_time(time_created),
        "tokens_input": tokens_input,
        "tokens_output": tokens_output,
        "tokens_cache_read": tokens_cache_read,
        "tokens_cache_write": tokens_cache_write,
        "tokens_total": tokens_total,
        "tokens_billable": tokens_input + tokens_output,
        "cost": round(cost or 0.0, 6),
        "wall_s": round((time_updated - time_created) / 1000, 1),
        "tool_calls": len(tools),
        "read_calls": len(read_paths),
        "distinct_read_files": len(set(read_paths)),
        "skill_calls": skill_calls,
        "tools": dict(Counter(tools)),
    }


def select_sessions(
    connection: sqlite3.Connection,
    args: argparse.Namespace,
) -> list[str]:
    if args.session_ids:
        return args.session_ids
    if args.parent:
        return [
            row[0]
            for row in connection.execute(
                "select id from session_v2 where parent_id = ? order by time_created",
                (args.parent,),
            )
        ]
    if args.recent:
        clauses: list[str] = []
        params: list[object] = []
        if args.directory:
            clauses.append("directory = ?")
            params.append(os.path.abspath(args.directory))
        if args.leaves:
            clauses.append(
                "id not in (select parent_id from session_v2 where parent_id is not null)"
            )
        sql = "select id from session_v2"
        if clauses:
            sql += " where " + " and ".join(clauses)
        sql += " order by time_updated desc limit ?"
        params.append(args.recent)
        return [row[0] for row in connection.execute(sql, params)]
    return []


def print_table(rows: list[dict], show_summary: bool) -> None:
    if not rows:
        print("no sessions found", file=sys.stderr)
        return

    header = (
        f"{'session':<28} {'title':<30} {'model':<18} "
        f"{'tokens':>10} {'bill':>8} {'tools':>5} {'reads':>5} {'wall':>7} {'skills':<26}"
    )
    print(header)
    print("-" * len(header))
    for row in rows:
        title = row["title"][:29]
        model = row["model"]
        if row["variant"] and row["variant"] != "default":
            model = f"{model}#{row['variant']}"
        skills = ",".join(row["skill_calls"]) or "-"
        print(
            f"{row['session']:<28} {title:<30} {model[:17]:<18} "
            f"{row['tokens_total']:>10,} {row['tokens_billable']:>8,} "
            f"{row['tool_calls']:>5} {row['read_calls']:>5} "
            f"{row['wall_s']:>6.1f}s {skills[:25]:<26}"
        )

    if not show_summary:
        return

    def median(key: str) -> float:
        return statistics.median(row[key] for row in rows)

    print("-" * len(header))
    print(
        f"n={len(rows)}  "
        f"median tokens={median('tokens_total'):,.0f}  "
        f"billable={median('tokens_billable'):,.0f}  "
        f"tools={median('tool_calls'):.0f}  "
        f"reads={median('read_calls'):.0f}  "
        f"wall={median('wall_s'):.1f}s  "
        f"cost={sum(row['cost'] for row in rows):.4f}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Collect OpenCode session token, tool, model, and timing metrics.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("session_ids", nargs="*", help="One or more session IDs.")
    parser.add_argument("--parent", help="Select every child session of this ID.")
    parser.add_argument("--recent", type=int, help="Select the N most recent sessions.")
    parser.add_argument(
        "--directory",
        help="With --recent, filter to this session directory.",
    )
    parser.add_argument(
        "--leaves",
        action="store_true",
        help="With --recent, omit sessions that have children (the parent run).",
    )
    parser.add_argument("--db", default=DEFAULT_DB, help=f"SQLite path (default: {DEFAULT_DB})")
    parser.add_argument("--json", action="store_true", help="Print JSON.")
    parser.add_argument("--csv", action="store_true", help="Print CSV.")
    parser.add_argument(
        "--no-summary",
        action="store_true",
        help="Omit the median summary from table output.",
    )
    args = parser.parse_args()

    if not args.session_ids and not args.parent and not args.recent:
        parser.print_help()
        return 2
    if args.json and args.csv:
        parser.error("choose --json or --csv, not both")

    connection = sqlite3.connect(f"file:{args.db}?mode=ro", uri=True)
    try:
        session_ids = select_sessions(connection, args)
        rows = []
        for session_id in session_ids:
            metrics = session_metrics(connection, session_id)
            if metrics is None:
                print(f"session not found: {session_id}", file=sys.stderr)
                continue
            rows.append(metrics)
    finally:
        connection.close()

    if args.json:
        print(json.dumps(rows, indent=2))
    elif args.csv:
        writer = csv.DictWriter(sys.stdout, fieldnames=CSV_FIELDS, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            record = dict(row)
            record["skill_calls"] = ",".join(record["skill_calls"])
            record["tools"] = json.dumps(record["tools"], sort_keys=True)
            writer.writerow(record)
    else:
        print_table(rows, not args.no_summary)
    return 0 if rows else 1


if __name__ == "__main__":
    raise SystemExit(main())
