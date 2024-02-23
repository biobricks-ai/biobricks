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
  
  @staticmethod
  def FromWorkingDirectory():
    """Get the local bb from the current working directory or its parents."""
    cwd = Path.cwd()
    if (cwd / ".bb").exists():
      return LocalBB(cwd)
    return None
        
  def get_depencies(self):
    """get bricks from the local bb dependencies file"""
    lines = self.dependencies_path.open("r").readlines()
    lines = [line.strip() for line in lines]
    return [Brick.Resolve(line) for line in lines]
  
  def add_dependency(self, ref: str):
      """add a dependency to the local bb dependencies file"""
      
      brickref = Brick.Resolve(ref)
      
      # check if the added dependency already exists
      bricknames = [brick.name for brick in self.get_depencies()]
      
      if brickref.name in bricknames:
          raise ValueError(
              f"'{brickref.name}' already exists. To update, run:\n"
              f"\t`biobricks remove {brickref.name}`\n"
              f"\tand then `biobricks add {brickref.name}`"
          )
      
      # add dependency to the dependencies file
      with open(self.dependencies_path, "a") as f:
          f.write(f"{brickref.url()}\n")

  def remove_dependency(self, ref: str):
      """Remove a dependency from the local bb dependencies file."""
      
      brickref = Brick.Resolve(ref)
      
      # Check if the dependency exists before attempting to remove it
      current_dependencies = self.get_depencies()
      bricknames = [brick.name for brick in current_dependencies]
      
      if brickref.name not in bricknames:
          raise ValueError(f"'{brickref.name}' does not exist in the dependencies.")
      
      # Create a new list excluding the dependency to be removed
      new_dependencies = [brick for brick in current_dependencies if brick.name != brickref.name]
      
      # Write the new list back to the dependencies file
      with open(self.dependencies_path, "w") as f:
          for brick in new_dependencies:
              f.write(f"{brick.url()}\n")

  
  def install_dependencies(self):
    """install all dependencies"""
    for brick in self.get_depencies():
      brick.install()
  