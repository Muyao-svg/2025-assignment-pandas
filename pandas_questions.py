"""
Plotting referendum results in pandas.

We want to make a beautiful map to report results of a referendum.
We would like to depict results with something similar to the maps
found here:
https://github.com/x-datascience-datacamp/datacamp-assignment-pandas/blob/main/example_map.png

To do that, we load the data as pandas.DataFrame, merge the info and
aggregate them by regions and finally plot them on a map using geopandas.
"""

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd


def load_data():
    """Load data from the CSV files referendum/regions/departments."""
    referendum = pd.read_csv("data/referendum.csv", sep=";")
    regions = pd.read_csv("data/regions.csv")
    departments = pd.read_csv("data/departments.csv")
    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    Output columns:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    regions_and_departments = departments.merge(
        regions,
        left_on="region_code",
        right_on="code",
        how="left",
    )

    regions_and_departments = regions_and_departments.rename(
        columns={
            "region_code": "code_reg",
            "name_x": "name_dep",
            "code_x": "code_dep",
            "name_y": "name_reg",
        }
    )

    cols = ["code_reg", "name_reg", "code_dep", "name_dep"]
    return regions_and_departments[cols]


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
    """Return a table with the absolute count for each region."""
    cols = [
        "Registered",
        "Abstentions",
        "Null",
        "Choice A",
        "Choice B",
    ]
    result = (
        referendum_and_areas.groupby("name_reg", as_index=False)[cols].sum()
    )
    return result


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum."""
    regions_geo = gpd.read_file("data/regions.geojson")

    regions_geo = regions_geo.merge(
        referendum_result_by_regions,
        left_on="nom",
        right_on="name_reg",
        how="left",
    )

    regions_geo["ratio"] = regions_geo["Choice A"] / (
        regions_geo["Choice A"] + regions_geo["Choice B"]
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
        df_reg,
        df_dep,
    )

    referendum_and_areas = merge_referendum_and_areas(
        referendum,
        regions_and_departments,
    )

    referendum_results = compute_referendum_result_by_regions(
        referendum_and_areas,
    )

    print(referendum_results)

    plot_referendum_map(referendum_results)
    plt.show()
