import pandas as pd
import simplekml


def create_kmz(boreholes_df, kmz_path):
    boreholes_kml = boreholes_df.groupby("Borehole ID")[["Latitude", "Longitude"]].first().reset_index()

    kml = simplekml.Kml()
    style = simplekml.Style()
    style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png'
    
    points = []
    for _, row in boreholes_kml.iterrows():
        pnt = kml.newpoint(coords=[(row['Longitude'], row['Latitude'])])
        pnt.style = style
        points.append(pnt)
    
    print(f"Number of points: {len(points)}")
    kml.savekmz(kmz_path)


if __name__ == "__main__":
    boreholes_uscs = pd.read_csv("../data/file_2_reUSCS_sampling_with_elevation.csv")
    create_kmz(boreholes_uscs, "../data/boreholes_uscs.kmz")
    