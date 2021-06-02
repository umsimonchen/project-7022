from rtree import index

class Rtree():
  def __init__(self):
    self.idx = index.Index()
    self.block_count = 0

  def get_rtree_index(self):
    return self.block_count, self.idx

  def update_index(self, point, action):    ## point: {id, lat, lon, name, action: (insert=0/delete=1)}
    if action == 0:
      self.idx.insert(point["id"], (point["lat"], point["lon"], point["lat"], point["lon"]), obj = point["name"])
      return "Insert Success"
    elif action == 1:
      self.idx.delete(point["id"], (point["lat"], point["lon"], point["lat"], point["lon"]))
      return "Delete Success"

  def get_nearest_k_point(self, input_loc, k):    ## input loc: {lat, lon}
    hits = self.idx.nearest((input_loc["lat"], input_loc["lon"], input_loc["lat"], input_loc["lon"]), k, objects = True)
    return hits