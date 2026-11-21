"""API server for the crane drawing generator."""
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response

import database
import drawing
from schemas import CraneInputs, DesignIn

app = FastAPI(title="Crane Drawing Generator")


@app.on_event("startup")
def startup():
    database.init_db()


def _svg(content):
    return Response(content=content, media_type="image/svg+xml")


@app.get("/api/designs")
def list_designs():
    return database.list_designs()


@app.post("/api/designs", status_code=201)
def create_design(design: DesignIn):
    return database.create_design(design.name, design.inputs.model_dump())


@app.get("/api/designs/{design_id}")
def get_design(design_id: int):
    design = database.get_design(design_id)
    if design is None:
        raise HTTPException(status_code=404, detail="Design not found")
    return design


@app.put("/api/designs/{design_id}")
def update_design(design_id: int, design: DesignIn):
    updated = database.update_design(design_id, design.name, design.inputs.model_dump())
    if updated is None:
        raise HTTPException(status_code=404, detail="Design not found")
    return updated


@app.delete("/api/designs/{design_id}", status_code=204)
def delete_design(design_id: int):
    if not database.delete_design(design_id):
        raise HTTPException(status_code=404, detail="Design not found")


@app.post("/api/preview")
def preview(inputs: CraneInputs):
    """Draw from inputs without saving."""
    return _svg(drawing.render_svg(inputs.model_dump(), "Preview"))


@app.get("/api/designs/{design_id}/drawing")
def design_drawing(design_id: int):
    design = database.get_design(design_id)
    if design is None:
        raise HTTPException(status_code=404, detail="Design not found")
    return _svg(drawing.render_svg(design["inputs"], design["name"]))


@app.get("/api/designs/{design_id}/dimensions")
def design_dimensions(design_id: int):
    """All computed sizes as numbers (mm)."""
    design = database.get_design(design_id)
    if design is None:
        raise HTTPException(status_code=404, detail="Design not found")
    return drawing.compute_dimensions(design["inputs"])
