"""Plotting referendum results in pandas.

In short, we want to make beautiful map to report results of a referendum. In
some way, we would like to depict results with something similar to the maps
that you can find here:
https://github.com/x-datascience-datacamp/datacamp-assignment-pandas/blob/main/example_map.png

To do that, you will load the data as pandas.DataFrame, merge the info and
aggregate them by regions and finally plot them on a map using `geopandas`.
"""
import geopandas as gpd
import matplotlib.pyplot as plt
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

def load_data():
    referendum = pd.read_csv(DATA_DIR / "referendum.csv", sep=";")
    regions = pd.read_csv(DATA_DIR / "regions.csv", sep=",")
    departments = pd.read_csv(DATA_DIR / "departments.csv", sep=",")
    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    region:id,code,name,slug
    department:id,region_code,code,name,slug

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    reg_dep = pd.merge(regions, departments,
             left_on='code', right_on='region_code',
             suffixes=('_reg', '_dep'),how='inner')
    reg_dep = reg_dep[['code_reg', 'name_reg', 'code_dep', 'name_dep']]
    return reg_dep


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame."""
    ref = referendum.copy()
    rad = regions_and_departments.copy()

    ref["Department code"] = (
        ref["Department code"]
        .astype(str)
        .str.strip()
        .str.replace(r"\.0$", "", regex=True)
        .str.zfill(2)
    )

    rad["code_dep"] = (
        rad["code_dep"]
        .astype(str)
        .str.strip()
        .str.replace(r"\.0$", "", regex=True)
        .str.zfill(2)
    )

    ref = ref[~ref["Department code"].str.contains("Z")]

    merged = ref.merge(
        rad,
        left_on="Department code",
        right_on="code_dep",
        how="inner",
    )

    return merged


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    grouped = referendum_and_areas.groupby(
        ['code_reg','name_reg'],
        as_index=True  # index by "code_reg" and "name_reg"
    ).agg({
        'Registered': 'sum',
        'Abstentions': 'sum',
        'Null': 'sum',
        'Choice A': 'sum',
        'Choice B': 'sum'
    })
    grouped = grouped.reset_index(level='name_reg')  # keep "name_reg" as a column
    grouped=grouped[["name_reg", "Registered", "Abstentions", "Null", "Choice A", "Choice B"]]
    return grouped


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    regions_geo = gpd.read_file("data/regions.geojson")
    regions_geo = regions_geo.merge(
        referendum_result_by_regions,
        left_on="nom",
        right_on="name_reg",
        how="left",
    )

    regions_geo["ratio"] = (
        regions_geo["Choice A"]
        / (regions_geo["Choice A"] + regions_geo["Choice B"])
    )

    regions_geo.plot(
        column="ratio",
        cmap="OrRd",
        legend=True,
    )

    return regions_geo

if __name__ == "__main__":

    referendum, df_reg, df_dep = load_data()
    regions_and_departments = merge_regions_and_departments(
        df_reg, df_dep
    )
    referendum_and_areas = merge_referendum_and_areas(
        referendum, regions_and_departments
    )
    referendum_results = compute_referendum_result_by_regions(
        referendum_and_areas
    )
    print(referendum_results)

    plot_referendum_map(referendum_results)
    plt.show()
