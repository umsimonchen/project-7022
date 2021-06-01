from rtree import index

class Rtree():
  def __init__(self):
    self.idx = index.Index()
    self.block_count = 0

  def get_rtree_index(self):
    return self.block_count, self.idx

  def update_index(self, point):    ## point: {id, lat, lng, name, action: (insert=0/delete=1)}
    if point["action"] == 0:
      self.idx.insert(point["id"], (point["lat"], point["lng"], point["lat"], point["lng"]), obj = point["name"])
      return "Insert Success"
    elif point["action"] == 1:
      self.idx.delete(point["id"], (point["lat"], point["lng"], point["lat"], point["lng"]))
      return "Delete Success"

  def get_nearest_k_point(self, input_loc, k):    ## input loc: {lat, lng}
    hits = self.idx.nearest((input_loc["lat"], input_loc["lng"], input_loc["lat"], input_loc["lng"]), object = True)
    return hits