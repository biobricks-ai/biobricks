from .brick import Brick
import os
from pathlib import Path

class LocalBB():
  
  def __init__(self, path):
    self.path = path / ".bb"
    self.dependencies_path = self.path / "dependencies.txt"
  
  @staticmethod
  def FromPath(path=os.getcwd()):
    return LocalBB(Path(path))
  
  def get_depencies(self):
    """get bricks from the local bb dependencies file"""
    lines = self.dependencies_path.open("r").readlines()
    return [Brick.Resolve(line) for line in lines]
  
  def add_dependency(self, ref: str):
    """add a dependency to the local bb dependencies file"""
    
    brickref = Brick.Resolve(ref)
    
    # check if the added dependency already exists
    bricknames = [brick.name for brick in self.get_depencies()]
    
    if brickref.name in bricknames:
      # TODO suggest update if updated version of ref exists
      print(f"'{brickref.name}' already exists, to update:")
      print(f"\trun `biobricks remove {brickref.name}`")
      print(f"\tand `biobricks add {brickref.name}`")
      return
    
    # add dependency to the dependencies file
    with open(self.dependencies_path, "a") as f:
      f.write(f"{brickref.url()}\n")
  