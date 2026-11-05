#!/usr/bin/env python3
"""Extract per-session efficiency metrics from the OpenCode SQLite store."""
import json, sqlite3, sys, os

DB = os.path.expanduser("~/.local/share/opencode/opencode.db")


def metrics(session_id):
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    row = con.execute(
        "select tokens_input,tokens_output,tokens_cache_read,tokens_cache_write,"
        "cost,time_created,time_updated,title,model from session_v2 where id=?",
        (session_id,),
    ).fetchone()
    if not row:
        return {"session": session_id, "error": "not found"}
    ti, to, tcr, tcw, cost, t0, t1, title, model_json = row
    model = json.loads(model_json) if model_json else {}
    msgs = con.execute(
        "select data from session_message where session_id=? order by seq", (session_id,)
    ).fetchall()
    tools, reads, skill_calls, paths = [], [], [], []
    text = []
    for (data,) in msgs:
        try:
            d = json.loads(data)
        except Exception:
            continue
        for c in d.get("content", []):
            if c.get("type") == "tool":
                name = c.get("name")
                tools.append(name)
                inp = (c.get("state") or {}).get("input") or {}
                if name == "skill":
                    skill_calls.append(inp)
                if name == "read":
                    p = inp.get("path")
                    if p:
                        reads.append(p)
                        paths.append(p)
                elif name in ("grep", "glob"):
                    p = inp.get("path")
                    if p:
                        paths.append(p)
            elif c.get("type") == "text":
                text.append(c.get("text", ""))
    con.close()
    return {
        "session": session_id,
        "title": title,
        "model": model.get("id"),
        "provider": model.get("providerID"),
        "variant": model.get("variant"),
        "tokens_input": ti,
        "tokens_output": to,
        "tokens_cache_read": tcr,
        "tokens_cache_write": tcw,
        "tokens_total": ti + to + tcr + tcw,
        "cost": cost,
        "wall_s": round((t1 - t0) / 1000, 1),
        "tool_calls": len(tools),
        "tool_names": tools,
        "read_calls": len(reads),
        "distinct_read_files": len(set(reads)),
        "distinct_paths_touched": len(set(paths)),
        "skill_calls": skill_calls,
        "answer": text[-1] if text else "",
    }


if __name__ == "__main__":
    ids = sys.argv[1:]
    if not ids:
        print("usage: measure.py <session-id> [...]", file=sys.stderr)
        sys.exit(2)
    print(json.dumps([metrics(i) for i in ids], indent=2))
