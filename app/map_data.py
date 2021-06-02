from pandana.loaders import osm
import pandas as pd

class Coordinate():
  def __init__(self):
    self.amenity_group = pd.DataFrame()

  def get_amenity_group(self):
    return self.amenity_group

  def check_amenity_group_none(self):
    return self.amenity_group.empty

  def make_amenity_group_to_none(self):
    self.amenity_group = None

# tag can choose: [restaurant, cafe, bar, school, university]
  def get_amenity_from_osm(self, lat_min, lon_min, lat_max, lon_max, type_name='restaurant'):
    amenity_group_total = osm.node_query(
      lat_min, lon_min, lat_max, lon_max, tags='"amenity"="%s"' % type_name)
    self.amenity_group = amenity_group_total[["lat", "lon", "name"]]
    return self.amenity_group

  def get_one_sample_from_amenity(self, amenity_group):
    sample = self.amenity_group.sample(1)
    result = {}
    for i in ["index", "lat", "lon", "name"]:
      value = getattr(sample, i).values[0]  # same as sample.#{key_name}.values[0]
      result[i] = value
    return result
