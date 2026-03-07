import time
import io
import zipfile
import logging
import os

import yaml
import jsonschema
from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from databricks.connect import DatabricksSession
spark = DatabricksSession.builder.serverless().getOrCreate()

app = FastAPI()
router = APIRouter(prefix="/api")


def load_contract(name: str) -> dict:
    path = f"/Volumes/3po/main/contracts/{name}.yaml"
    with open(path, "r") as f:
        return yaml.safe_load(f)


def validate_records(records: list[dict], contract_name: str):
    schema = load_contract(contract_name)
    row_schema = schema.get("items", schema)
    errors = []
    for i, record in enumerate(records):
        try:
            jsonschema.validate(instance=record, schema=row_schema)
        except jsonschema.ValidationError as e:
            errors.append(f"Row {i}: {e.message}")
    if errors:
        raise HTTPException(
            status_code=502,
            detail={"message": f"Contract '{contract_name}' violations", "errors": errors[:10]},
        )


@app.get("/ingests")
def ingests(start: int = 0, end: int = None):
    if end is None:
        end = int(time.time())
    df = spark.table("3po.main.ingests")
    filtered = df.filter((df.time >= start) & (df.time <= end))
    records = filtered.toPandas().to_dict(orient="records")
    validate_records(records, "ingests")
    return records


@app.get("/timeline")
def timeline(start: int = 0, end: int = None):
    if end is None:
        end = int(time.time())
    df = spark.table("3po.main.timeline")
    filtered = df.filter((df.time >= start) & (df.time <= end))
    records = filtered.toPandas().to_dict(orient="records")
    validate_records(records, "timeline")   # ← fixed contract name
    return records


@app.get("/timestamp/{platform}/{time}")
def timestamp(platform: str, time: int):
    table = f"3po.t{platform}.t{time}"
    df = spark.table(table)
    records = df.toPandas().to_dict(orient="records")
    validate_records(records, "timestamp")  # ← fixed contract name
    return records


@app.get("/history/{platform}/{id}")
def history(platform: str, id: str):
    table = f"3po.h{platform}.h{id}"
    df = spark.table(table)
    records = df.toPandas().to_dict(orient="records")
    validate_records(records, "history")    # ← fixed contract name
    return records


@app.get("/positivity/{platform}")
def positivity(platform: str):
    table = f"3po.main.{platform}_positivity"
    df = spark.table(table)
    records = df.toPandas().to_dict(orient="records")
    validate_records(records, "positivity") # ← fixed contract name
    return records


@app.get("/positivity/{platform}/{id}")
def monopositivity(platform: str, id: str):
    df = spark.table(f"3po.main.{platform}_positivity")
    row = df.filter(df.id == id).select("positivity").first()
    return row["positivity"] if row else None


@app.get("/content/{platform}/{id}")
def content(platform: str, id: str):
    volume_path = f"/Volumes/3po/c{platform}/{id}"
    # Use native Python — /Volumes paths are directly accessible in Databricks Apps
    import pathlib
    files = list(pathlib.Path(volume_path).iterdir())
    if len(files) == 1:
        return FileResponse(str(files[0]))
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as zf:
        for f in files:
            with open(f, "rb") as file:
                zf.writestr(f.name, file.read())
    buffer.seek(0)
    return StreamingResponse(buffer, media_type="application/zip", headers={
        "Content-Disposition": f"attachment; filename={id}.zip"
    })
