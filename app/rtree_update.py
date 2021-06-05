from rtree import index
import hashlib
import json

class Rtree():
  def __init__(self):
    self.init_idx()

  ## query from idx
  def get_rtree_index(self):
    return self.idx

  def init_idx(self):
    self.idx = index.Index()

  def get_nearest_k_points(self, blockchain, lat, lon, k, types):    ## input loc: {lat, lon}
    block = self.find_block(blockchain, lat, lon, types)
    if block == None: return []
    self.update_index(block)
    hits = self.idx.nearest((lat, lon, lat, lon), k, objects = True)
    k_point_result = []
    item_count = 0
    for item in hits:
      if item_count >= k: break
      point = {
        "id": item.id,
        "lat": item.bbox[0],
        "lon": item.bbox[1],
        "name": item.object
      }
      k_point_result.append(point)
      item_count += 1
    return k_point_result

  def find_block(self, blockchain, lat, lon, types):
    for block in blockchain.chain:
      block_remark = block["remark"]
      if block_remark == {}: continue
      result = remark_checking(block_remark, lat, lon, types)
      if result == True: return block
    return None

  def update_index(self, block):
    self.init_idx()
    for point in block['transactions']:                  ## point: {id, lat, lon, name}
      self.idx.insert(point["id"], (point["lat"], point["lon"], point["lat"], point["lon"]), obj = point["name"])
    return True

def remark_checking(remark, lat, lon, types):
  if types == remark["types"]:
    if remark["lat_min"] < lat < remark["lat_max"] and remark["lon_min"] < lon < remark["lon_max"]:
      return True
  return False