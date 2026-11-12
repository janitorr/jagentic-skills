# Orders API

A small FastAPI service that serves orders to the storefront and the partner
portal.

## Commands

- Test: `python3 -m unittest discover -s tests -v`
- Run: `uvicorn app.main:app`

## Environment

- Tracker: local files; `issue.md` is the originating issue.
- Approval marker: the file `APPROVED` in the change directory.
- Review destination: stdout.
- Workspace: current directory; base branch `main`; do not push or open a pull
  request.
