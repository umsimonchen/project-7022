from rtree import index

class Rtree():
  def __init__(self):
    self.idx = index.Index()
    self.block_count = 0

  def get_rtree_index(self):
    return self.block_count, self.idx

  def update_index(self, point, action):    ## point: {id, lat, lon, name}, action: (insert=0/delete=1)
    if action == 0:
      self.idx.insert(point["id"], (point["lat"], point["lon"], point["lat"], point["lon"]), obj = point["name"])
      return "Insert Success"
    elif action == 1:
      self.idx.delete(point["id"], (point["lat"], point["lon"], point["lat"], point["lon"]))
      return "Delete Success"

  def get_nearest_k_points(self, lat, lon, k):    ## input loc: {lat, lon}
    hits = self.idx.nearest((lat, lon, lat, lon), k, objects = True)
    k_point_result = []
    for item in hits:
      point = {
        "id": item.id,
        "lat": item.bbox[0],
        "lon": item.bbox[1],
        "name": item.object
      }
      k_point_result.append(point)
    return k_point_result