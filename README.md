# CraneDraft – Crane Drawing Generator

A small web app that makes a 2D drawing of a single girder overhead (EOT) crane from three inputs: load, span and lifting height. The drawing has a front view, a plan view and a technical data table, all with labelled dimensions. Designs can be saved, listed, opened, edited and deleted.

## How to run

Needs Python 3.10 or newer.

```
pip install -r requirements.txt
python -m uvicorn main:app --reload
```

Then open:

- App: http://127.0.0.1:8000
- API docs (try every endpoint): http://127.0.0.1:8000/docs

The database file `cranes.db` is created automatically on first start.

If you change the code and the page does not update, stop the server (Ctrl+C) and start it again. On Windows the `--reload` option sometimes gets stuck.

## Stack and why

- **Python + FastAPI** for the backend. Quick to build, and it checks inputs automatically with Pydantic and gives a free API docs page.
- **SQLite** for the database. One file, nothing to install, enough for this size.
- **SVG** for the drawing, made on the server. It is just text, so it is easy to generate and test, it shows in any browser, and it stays sharp when zoomed.
- **Plain HTML + JavaScript** for the page. No build step, so the app runs with one command.

## API

| Method | Path | What it does |
|---|---|---|
| GET | /api/designs | List saved designs |
| POST | /api/designs | Save a new design |
| GET | /api/designs/{id} | Get one design |
| PUT | /api/designs/{id} | Edit a design |
| DELETE | /api/designs/{id} | Delete a design |
| POST | /api/preview | Draw from inputs without saving |
| POST | /api/dimensions | All computed sizes from inputs, without saving |
| GET | /api/designs/{id}/drawing | Drawing of a saved design (SVG) |
| GET | /api/designs/{id}/dimensions | All computed sizes as numbers |

Bad inputs (out of range, missing, wrong type) return 422 with a message for each field. Unknown ids return 404.

## Files

- `main.py` – API routes
- `schemas.py` – input rules and allowed ranges (server-side validation)
- `database.py` – SQLite save / list / get / update / delete
- `drawing.py` – turns inputs into dimensions and draws the SVG
- `static/index.html` – the web page

## Known limitations

- Most sizes that are not user inputs (crane height above rail 1369, hook to rail 810, wheelbase 3800, end carriage 4310, clearances) are copied from the one reference drawing (10 t, 25 m). They do not change with load or span, so they are wrong for very different cranes. They are marked as estimates in the code and on the drawing.
- The input ranges are my estimates, not from a standard.
- No structural checks (girder strength, deflection, wheel loads).
- Only single girder cranes. No side view (section A-A).
- No users or login. Everyone sees all designs.
- No export to PDF or DXF. The drawing can be downloaded as SVG with the SVG button.
