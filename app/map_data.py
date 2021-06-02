from pandana.loaders import osm

class Coordinate():
  def __init__(self):
    self.amenity_group = None

  def get_amenity_group(self):
    return self.amenity_group

  def check_amenity_group_none(self):
    return self.amenity_group == None

# tag can choose: [restaurant, cafe, bar, school, university]
  def get_amenity_from_osm(self, lat_min, lng_min, lat_max, lng_max, type_name='restaurant'):
    amenity_group_total = osm.node_query(
      lat_min, lng_min, lat_max, lng_max, tags='"amenity"="%s"' % type_name)
    self.amenity_group = amenity_group_total[["lat", "lng", "name"]]
    return self.amenity_group

  def get_one_sample_from_amenity(self, amenity_group):
    sample = self.amenity_group.sample(1)
    result = {}
    for i in ["index", "lat", "lng", "name"]:
      value = getattr(sample, i).values[0]  # same as sample.#{key_name}.values[0]
      result[i] = value
    return result