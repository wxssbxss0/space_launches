import pytest
import json
from src import api

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_help(client):
    rv = client.get("/help")
    assert rv.status_code == 200

def test_post_and_get_data(client):
    data = {
        "Company Name": "SpaceX",
        "Location": "LC-39A, Kennedy Space Center, Florida, USA",
        "Detail": "Falcon 9 Block 5 | Starlink V1 L9 & BlackSky",
        "Status Rocket": "StatusActive",
        "Rocket": "50.0",
        "Status Mission": "Success",
        "Country of Launch": "USA",
        "Companys Country of Origin": "USA",
        "Private or State Run": "P",
        "DateTime": "2020-08-07 05:12:00+00:00",
        "Year": "2020",
        "Month": "08",
        "Day": "07",
        "Date": "07/08/2020",
        "Time": "05:12"
    }
    rv = client.post("/data", json=data)
    assert rv.status_code == 201
    rv = client.get("/data")
    assert rv.status_code == 200
    assert "SpaceX" in rv.data.decode()

def test_timeline_job(client):
    rv = client.post("/analyze/timeline")
    assert rv.status_code == 202
    assert "job_id" in rv.get_json()

def test_sector_job(client):
    rv = client.post("/analyze/sector")
    assert rv.status_code == 202
    assert "job_id" in rv.get_json()

def test_geography_job(client):
    rv = client.post("/analyze/geography")
    assert rv.status_code == 202
    assert "job_id" in rv.get_json()

def test_job_status_not_found(client):
    rv = client.get("/jobs/doesnotexist")
    assert rv.status_code == 404

