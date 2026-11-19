"""Join released inspections and public locations using the province's structure codes."""
import csv
from datetime import date
import io
import re
import subprocess
from source_io import ROOT, archives, archived, fetch, publish

REGISTRY = "https://data.novascotia.ca/api/views/gs26-c3fm/rows.csv?accessType=DOWNLOAD"
ROW = re.compile(r"^\s*((?:ANN|HFX)\d+[A-Z]?)\s+(.+?)\s+Level\s+(1|2v?)\s+(\d{4}-\d{2}-\d{2})\s+(NULL|\d+)\s+([01])\s+(\S+)\s*$")

def normal_id(value):
    match = re.fullmatch(r"([A-Z]+)0*(\d+)([A-Z]?)", value.strip().upper())
    return (match[1],int(match[2]),match[3]) if match else None


def assemble(pdf, locations):
    reports = archives()
    pages = subprocess.run(["pdftotext","-layout","-","-"],input=pdf,stdout=subprocess.PIPE,check=True).stdout.decode().split("\f")
    bridges = {}
    visits = {}

    def add(identifier, name, level, day, rating, finalised, in_error, release, page):
        date.fromisoformat(day)
        if rating is not None and (type(rating) != int or not 0 <= rating <= (3 if level == "1" else 9)):
            raise ValueError("Rating outside source scale")
        bridge = bridges.setdefault(identifier,dict(id=identifier,name=name,visits=[]))
        # Two extracts can repeat an inspection with changed finalisation or rating. Retain both versions.
        key = (identifier, level, day, rating, finalised)
        record = visits.get(key)
        evidence = dict(release=release, page=page, inError=in_error)
        if record is None:
            record = dict(level=level, date=day, rating=rating, finalised=finalised, evidence=[])
            bridge["visits"].append(record)
            visits[key] = record
        if evidence not in record["evidence"]:
            record["evidence"].append(evidence)

    for page_number, page in enumerate(pages,1):
        for line in page.splitlines():
            if not re.match(r"^\s*(ANN|HFX)\d+",line):
                continue
            row = ROW.match(line)
            if not row:
                raise ValueError(f"Unrecognised inspection row on PDF page {page_number}")
            identifier,name,level,day,rating,finalised,_ = row.groups()
            add(identifier," ".join(name.split()),level,day,None if rating=="NULL" else int(rating),bool(int(finalised)),None,2020,page_number)
    with (ROOT/"sources/reviewed-2023.csv").open() as source:
        for row in csv.DictReader(source):
            identifier = row["id"]
            add(identifier,bridges[identifier]["name"],row["level"],row["date"],int(row["rating"]) if row["rating"] else None,
                bool(int(row["finalised"])),bool(int(row["in_error"])),2023,int(row["page"]))
    by_id = {}
    for row in csv.DictReader(io.StringIO(locations.decode("utf-8-sig"))):
        key = normal_id(row["StructureID"])
        if key and key[0] in ("HFX", "ANN"):
            by_id.setdefault(key,[]).append(row)
    for identifier,b in bridges.items():
        matched = by_id.get(normal_id(identifier),[])
        if len(matched) == 1:
            row=matched[0]
            if row["Latitude"] and row["Longitude"]:
                lat,lon=float(row["Latitude"]),float(row["Longitude"])
                if 42 < lat < 48 and -67 < lon < -59:
                    b.update(registryId=row["StructureID"], location=[lat,lon])
        b["visits"].sort(key=lambda v:(v["date"],v["level"]),reverse=True)
    if len(bridges)<400 or not bridges["ANN002"].get("location"):
        raise ValueError("Inspection or location source is incomplete")
    return dict(start=2020,end=2023,coverage="Halifax and Annapolis · 2020 and 2023 releases",
                count=len(visits),bridges=list(bridges.values()),sources={str(y):s["url"] for y,s in zip([2020,2023],reports)})


if __name__ == "__main__":
    older,newer = archives()
    pdf = archived(older)
    archived(newer)
    publish(assemble(pdf,fetch(REGISTRY)))
