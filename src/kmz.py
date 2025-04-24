import simplekml


def create_kmz(boreholes_df, kmz_path):
    boreholes_kml = boreholes_df.groupby("Borehole ID")[["Latitude", "Longitude"]].first().reset_index()

    kml = simplekml.Kml()
    points = []
    for _, row in boreholes_kml.iterrows():
        points.append(kml.newpoint(
            coords=[(row["Longitude"], row["Latitude"])],
        ))
    
    kml.savekmz(kmz_path)
    