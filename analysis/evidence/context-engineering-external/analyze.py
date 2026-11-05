#!/usr/bin/env python3
import json, sqlite3, os, re, statistics as st

DB = os.path.expanduser("~/.local/share/opencode/opencode.db")
PARENT = "ses_e535c7922ffeHoIwa0qC2Ym6r4"
OUT = os.environ.get(
    "METRICS_OUT",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "metrics.json"),
)


def parse_title(t):
    t = t or ""
    if t.lower().startswith("pilot"):
        cond = "skill" if "skill" in t.lower() else "control"
        return ("code", "Nagger", cond, 1)
    study = "docs" if " docs " in t.lower() else "code"
    m = re.match(r"(Nagger|Mittens|OAC) (?:docs )?(control|skill|primed) r(\d+)", t)
    if not m:
        return None
    return (study, m.group(1), m.group(2), int(m.group(3)))


def metrics(sid):
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    row = con.execute(
        "select tokens_input,tokens_output,tokens_cache_read,tokens_cache_write,cost,"
        "time_created,time_updated,model from session_v2 where id=?", (sid,)
    ).fetchone()
    ti, to, tcr, tcw, cost, t0, t1, model_json = row
    model = json.loads(model_json) if model_json else {}
    tools, reads, skill = [], [], []
    text = []
    for (data,) in con.execute("select data from session_message where session_id=? order by seq", (sid,)):
        d = json.loads(data)
        for c in d.get("content", []):
            if c.get("type") == "tool":
                tools.append(c.get("name"))
                inp = (c.get("state") or {}).get("input") or {}
                if c.get("name") == "read" and inp.get("path"):
                    reads.append(inp["path"])
                if c.get("name") == "skill":
                    skill.append(inp.get("id"))
            elif c.get("type") == "text":
                text.append(c.get("text", ""))
    con.close()
    return dict(
        model=model.get("id"), provider=model.get("providerID"),
        variant=model.get("variant"),
        tokens_input=ti, tokens_output=to, tokens_cache_read=tcr, tokens_cache_write=tcw,
        tokens_total=ti + to + tcr + tcw, tokens_billable=ti + to, cost=cost,
        wall_s=round((t1 - t0) / 1000, 1), tool_calls=len(tools),
        read_calls=len(reads), distinct_read_files=len(set(reads)),
        skill_calls=skill, answer=text[-1] if text else "",
    )


RUBRIC = {
    ("code", "Nagger"): ["TaskEndpoints", "CompleteOneShotTaskCommand", "ITaskStore", "SqliteTaskStore", "TaskItem"],
    ("code", "Mittens"): ["FactMcpTools", "MittensSet", "UpsertFact", "FactWriter", "MittensFacts", "Fact.cs"],
    ("code", "OAC"): ["registry.json", "install.sh", "components", "auto-detect", "agent"],
    ("docs", "Nagger"): ["timezone", "seven", "ordering", "read-only", "CHANGELOG"],
    ("docs", "Mittens"): ["MemoryFacts", "MittensFacts", "conflict", "secret", "FromSqlRaw"],
    ("docs", "OAC"): ["registry.json", "install.sh", "profile", "contexts", "gap"],
}

rows = []
con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
for sid, title in con.execute("select id,title from session_v2 where parent_id=? order by time_created", (PARENT,)):
    p = parse_title(title)
    if not p:
        print("UNPARSED", sid, title)
        continue
    study, repo, cond, rep = p
    m = metrics(sid)
    m.update(session=sid, title=title, study=study, repo=repo, condition=cond, rep=rep)
    keys = RUBRIC[(study, repo)]
    low = m["answer"].lower()
    hits = sum(1 for k in keys if k.lower() in low)
    m["rubric_hits"] = hits
    m["rubric_n"] = len(keys)
    m["rubric"] = round(hits / len(keys), 2)
    rows.append(m)
con.close()

with open(OUT, "w") as f:
    json.dump(rows, f, indent=2)

# flat table
hdr = ["study", "repo", "cond", "rep", "tok_total", "tok_bill", "cache_rd", "tools", "reads", "files", "wall", "rubric", "skill"]
print("\t".join(hdr))
for r in sorted(rows, key=lambda x: (x["study"], x["repo"], x["condition"], x["rep"])):
    print("\t".join(map(str, [r["study"], r["repo"], r["condition"], r["rep"], r["tokens_total"],
                              r["tokens_billable"], r["tokens_cache_read"], r["tool_calls"], r["read_calls"],
                              r["distinct_read_files"], r["wall_s"], r["rubric"], ",".join(r["skill_calls"]) or "-"])))

print("\n=== medians by study/repo/condition ===")
groups = {}
for r in rows:
    groups.setdefault((r["study"], r["repo"], r["condition"]), []).append(r)
for key in sorted(groups):
    g = groups[key]
    def med(k): return round(st.median([x[k] for x in g]), 1)
    print(key, "n=", len(g),
          "tok_total=", med("tokens_total"), "tok_bill=", med("tokens_billable"),
          "cache=", med("tokens_cache_read"), "tools=", med("tool_calls"),
          "reads=", med("read_calls"), "files=", med("distinct_read_files"),
          "wall=", med("wall_s"), "rubric=", med("rubric"),
          "skill=", sum(1 for x in g if x["skill_calls"]))

print("\n=== overall by study/condition ===")
for key in sorted(set((r["study"], r["condition"]) for r in rows)):
    g = [r for r in rows if (r["study"], r["condition"]) == key]
    def med(k): return round(st.median([x[k] for x in g]), 1)
    print(key, "n=", len(g), "tok_total=", med("tokens_total"), "tok_bill=", med("tokens_billable"),
          "tools=", med("tool_calls"), "reads=", med("read_calls"),
          "files=", med("distinct_read_files"), "wall=", med("wall_s"), "rubric=", med("rubric"))
