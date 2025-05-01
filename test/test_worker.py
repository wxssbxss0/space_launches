import pytest
import pandas as pd

from worker import (
    plot_private_crossover,  # renamed
    plot_sector,
    plot_geography,
    plot_top_private
)

@pytest.fixture

def sample_df():
    data = [
        {"Year": "2020", "Private or State Run": "P", "Country of Launch": "USA"},
        {"Year": "2019", "Private or State Run": "S", "Country of Launch": "China"},
        {"Year": "2020", "Private or State Run": "S", "Country of Launch": "USA"},
        {"Year": "2018", "Private or State Run": "P", "Country of Launch": "Russia"},
    ]
    return pd.DataFrame(data)

@pytest.fixture

def sample_records():
    return [
        {"id": "1", "Year": "1996", "Private or State Run": "P", "Company Name": "CompA"},
        {"id": "2", "Year": "1997", "Private or State Run": "P", "Company Name": "CompA"},
        {"id": "3", "Year": "1998", "Private or State Run": "P", "Company Name": "CompB"},
        {"id": "4", "Year": "1999", "Private or State Run": "S", "Company Name": "CompC"},
        {"id": "5", "Year": "2000", "Private or State Run": "P", "Company Name": "CompB"},
        {"id": "6", "Year": "2020", "Private or State Run": "P", "Company Name": "CompD"},
    ]


def test_plot_private_crossover(sample_records):
    img = plot_private_crossover(sample_records)
    assert isinstance(img, (bytes, bytearray))
    assert img.startswith(b"\x89PNG\r\n\x1a\n")


def test_plot_sector(sample_df):
    img = plot_sector(sample_df)
    assert isinstance(img, (bytes, bytearray))
    assert img.startswith(b"\x89PNG\r\n\x1a\n")


def test_plot_geography(sample_df):
    img = plot_geography(sample_df)
    assert isinstance(img, (bytes, bytearray))
    assert img.startswith(b"\x89PNG\r\n\x1a\n")


def test_plot_top_private(sample_records):
    img = plot_top_private(sample_records)
    assert isinstance(img, (bytes, bytearray))
    assert img.startswith(b"\x89PNG\r\n\x1a\n")

