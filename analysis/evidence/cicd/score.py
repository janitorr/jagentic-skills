#!/usr/bin/env python3
"""Extract CI/CD rubric signals from one run directory.

Usage: python3 analysis/evidence/cicd/score.py /tmp/opencode/work/orders-api-7

Prints evidence, not a score. The rubric is judged manually against the
official docs cited in analysis/evidence/cicd.md.
"""

import json
import re
import sys
from pathlib import Path

import yaml

SHA = re.compile(r"@[0-9a-f]{40}$")


def load(path):
    return yaml.safe_load(path.read_text())


def github_steps(doc):
    for job_id, job in (doc.get("jobs") or {}).items():
        for step in job.get("steps") or []:
            yield job_id, step


def main():
    run = Path(sys.argv[1])
    workflows = []
    for path in sorted((run / ".github/workflows").glob("*.y*ml")):
        doc = load(path)
        workflows.append(
            {
                "file": path.name,
                "name": doc.get("name"),
                "triggers": doc.get("on", doc.get(True)),
                "permissions": doc.get("permissions"),
                "concurrency": doc.get("concurrency"),
                "jobs": [
                    {
                        "id": job_id,
                        "needs": job.get("needs"),
                        "environment": job.get("environment"),
                        "timeout": job.get("timeout-minutes"),
                        "permissions": job.get("permissions"),
                        "uses": [s.get("uses") for s in job.get("steps") or [] if s.get("uses")],
                    }
                    for job_id, job in (doc.get("jobs") or {}).items()
                ],
            }
        )

    az_path = run / "azure-pipelines.yml"
    azure = None
    if az_path.exists():
        doc = load(az_path)
        stages = []
        for stage in doc.get("stages") or []:
            jobs = []
            for job in stage.get("jobs") or []:
                kind = "deployment" if "deployment" in job else "job"
                hooks = []
                strategy = job.get("strategy") or {}
                for name, hook in (strategy.get("runOnce") or {}).items():
                    if isinstance(hook, dict):
                        hooks.append(
                            {
                                "hook": name,
                                "steps": [
                                    s.get("task") or s.get("script", "")[:80]
                                    for s in hook.get("steps") or []
                                ],
                            }
                        )
                jobs.append(
                    {
                        "kind": kind,
                        "name": job.get(kind),
                        "environment": job.get("environment"),
                        "timeout": job.get("timeoutInMinutes"),
                        "condition": job.get("condition"),
                        "strategy": list(strategy),
                        "hooks": hooks,
                        "tasks": [s.get("task") for s in job.get("steps") or [] if s.get("task")],
                    }
                )
            stages.append(
                {
                    "name": stage.get("stage"),
                    "dependsOn": stage.get("dependsOn"),
                    "condition": stage.get("condition"),
                    "jobs": jobs,
                }
            )
        azure = {
            "triggers": doc.get("trigger"),
            "pr": doc.get("pr"),
            "parameters": [p.get("name") for p in doc.get("parameters") or []],
            "stages": stages,
        }

    all_text = "\n".join(
        p.read_text()
        for p in run.rglob("*")
        if p.is_file() and p.suffix in (".yml", ".yaml", ".sh") and ".git" not in p.parts
    )
    uses = [u for wf in workflows for job in wf["jobs"] for u in job["uses"]]
    third_party = [u for u in uses if not u.startswith("./")]
    signals = {
        "uses_total": len(third_party),
        "uses_sha_pinned": sum(1 for u in third_party if SHA.search(u)),
        "uses_tag_pinned": [u for u in third_party if not SHA.search(u)],
        "local_actions": [u for u in uses if u.startswith("./")],
        "upload_artifact": all_text.count("upload-artifact"),
        "publish_test_results": all_text.count("PublishTestResults"),
        "publish_pipeline_artifact": all_text.count("PublishPipelineArtifact"),
        "coverage_mentions": len(re.findall(r"coverage|cobertura|junit", all_text, re.I)),
        "health_checks": len(re.findall(r"/health|healthcheck|health check", all_text, re.I)),
        "rollback_mentions": len(re.findall(r"rollback", all_text, re.I)),
        "docker_build_push": all_text.count("build-push-action"),
        "azure_docker_tasks": all_text.count("Docker@"),
        "condition_template_wrapped": len(re.findall(r"condition:\s*\$\{\{", all_text)),
        "persist_credentials_false": all_text.count("persistCredentials: false"),
        "oidc_login": all_text.count("azure/login"),
    }

    print(json.dumps({"run": str(run), "github": workflows, "azure": azure, "signals": signals}, indent=2))


if __name__ == "__main__":
    main()
