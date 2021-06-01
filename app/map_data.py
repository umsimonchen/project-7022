from pandana.loaders import osm

class Coordinate():
# tag can choose: [restaurant, cafe, bar, school, university]
  def get_amenity_from_osm(self, lat_min, lng_min, lat_max, lng_max, type_name='restaurant'):
    amenity_group = osm.node_query(
      lat_min, lng_min, lat_max, lng_max, tags='"amenity"="%s"' % type_name)
    return amenity_group[["lat", "lon", "name"]]

  def get_one_sample_from_amenity(self, amenity_group):
    sample = amenity_group.sample(1)
    result = {}
    for i in ["index", "lat", "lon", "name"]:
      value = getattr(sample, i).values[0]  # same as sample.#{key_name}.values[0]
      result[i] = value
    return result