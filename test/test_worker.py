import pytest
import pandas as pd
from worker import plot_timeline, plot_sector, plot_geography

@pytest.fixture
def sample_df():
    data = [
        {"Year": "2020", "Private or State Run": "P", "Country of Launch": "USA"},
        {"Year": "2019", "Private or State Run": "S", "Country of Launch": "China"},
        {"Year": "2020", "Private or State Run": "S", "Country of Launch": "USA"},
        {"Year": "2018", "Private or State Run": "P", "Country of Launch": "Russia"},
    ]
    return pd.DataFrame(data)

def test_plot_timeline(sample_df):
    img = plot_timeline(sample_df)
    assert isinstance(img, bytes)
    assert len(img) > 0

def test_plot_sector(sample_df):
    img = plot_sector(sample_df)
    assert isinstance(img, bytes)
    assert len(img) > 0

def test_plot_geography(sample_df):
    img = plot_geography(sample_df)
    assert isinstance(img, bytes)
    assert len(img) > 0
