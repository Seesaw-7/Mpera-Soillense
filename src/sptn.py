import pandas as pd
from density_consistency import get_density


def get_filtered_boreholes(sptn, layering, max_depth_diff=10, sptn_threshold=45):
    uscs_range = layering.groupby("Borehole ID").agg(
        borehole_top_depth=("Top Depth", "min"),
        borehole_bottom_depth=("Bottom Depth", "max")
    )
    sptn_range = sptn.groupby("Borehole ID")['Test Depth'].agg(
        spt_top_depth="min",
        spt_bottom_depth="max"
    )
    range = pd.merge(uscs_range, sptn_range, on=["Borehole ID"], how="inner")
    boreholes_near_top = range[
        abs(range["spt_top_depth"] - range["borehole_top_depth"]) <= max_depth_diff
    ].index
    boreholes_near_bottom = range[
        abs(range["borehole_bottom_depth"] - range["spt_bottom_depth"]) <= max_depth_diff
    ].index

    sptn_bottom = sptn.loc[sptn.groupby('Borehole ID')['Test Depth'].idxmax()]
    boreholes_high_sptn = sptn_bottom.loc[sptn_bottom["SPTN"] >= sptn_threshold, "Borehole ID"]

    return set(boreholes_near_top) & (
        set(boreholes_near_bottom) | set(boreholes_high_sptn)
    )


def merge_all(boreholes, layering, sptn, filtered_boreholes):
    uscs_sptn = pd.merge(sptn, layering, on=["Borehole ID"], how="inner")
    
    # If the test depth is right at the junction of two layers, it is assigned to the lower layer.
    uscs_sptn = uscs_sptn[(uscs_sptn["Test Depth"] >= uscs_sptn["Top Depth"]) & 
                          (uscs_sptn["Test Depth"] < uscs_sptn["Bottom Depth"])]
    # If the test depth is right at the junction of two layers, it is assigned to both layers.
    # uscs_sptn = uscs_sptn[(uscs_sptn["Test Depth"] >= uscs_sptn["Top Depth"]) &
    #                       (uscs_sptn["Test Depth"] <= uscs_sptn["Bottom Depth"])]
    uscs_sptn_filtered = uscs_sptn[uscs_sptn["Borehole ID"].isin(filtered_boreholes)]

    boreholes_uscs_sptn = pd.merge(boreholes, uscs_sptn_filtered, on=["Borehole ID"], how="right")

    # Convert depth to elevation
    boreholes_uscs_sptn["Top Depth"] = boreholes_uscs_sptn["Elevation"] - boreholes_uscs_sptn["Top Depth"]
    boreholes_uscs_sptn["Bottom Depth"] = boreholes_uscs_sptn["Elevation"] - boreholes_uscs_sptn["Bottom Depth"]
    boreholes_uscs_sptn["Test Depth"] = boreholes_uscs_sptn["Elevation"] - boreholes_uscs_sptn["Test Depth"]

    # Add a column for density/consistency
    boreholes_uscs_sptn['Density / Consistency'] = boreholes_uscs_sptn.apply(
        lambda row: get_density(row['USCS'], row['SPTN']), axis=1
    )

    # Rename the columns
    boreholes_uscs_sptn.rename(
        columns={
            "Elevation": "Elevation (ft)",
            "Borehole Test ID": "In-situ Test #",
            "Test Depth": "Test Elevation (ft)",
            "Sub Borehole Layer": "Layer #",
            "Top Depth": "Layer Top Elevation (ft)",
            "Bottom Depth": "Layer Bottom Elevation (ft)",
            "Description": "Soil Description",
        },
        inplace=True
    )
    
    return boreholes_uscs_sptn


if __name__ == "__main__":
    boreholes = pd.read_csv("../../file_1.csv")
    boreholes = boreholes.iloc[:, [0, 3, 4, 5]]
    boreholes.columns = ["Borehole ID", "Latitude", "Longitude", "Elevation"]
    layering_columns = [
        "Borehole ID", "Sub Borehole Layer", "Top Depth", "Bottom Depth", 
        "Description", "Lithology", "USCS"
    ]
    layering = pd.read_csv("../../file_2_reUSCS.csv", usecols=layering_columns)
    sptn = pd.read_csv("../../file_3.csv").drop(columns=["Document ID", "Latitude", "Longitude"])
    sptn = sptn.dropna()

    filtered_boreholes = get_filtered_boreholes(sptn, layering)
    boreholes_uscs_sptn = merge_all(boreholes, layering, sptn, filtered_boreholes)
    boreholes_uscs_sptn.to_csv("../data/boreholes_reuscs_sptn.csv", index=False)
