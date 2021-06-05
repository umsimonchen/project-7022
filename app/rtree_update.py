from rtree import index
import hashlib
import json

class Rtree():
  def __init__(self):
    self.idx = index.Index()

  ## query from idx
  def get_rtree_index(self):
    return self.idx

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

  # change the future_idx_temp
  def update_index(self, point):    ## point: {id, lat, lon, name}
    self.idx.insert(point["id"], (point["lat"], point["lon"], point["lat"], point["lon"]), obj = point["name"])
    return True