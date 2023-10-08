from .brick import Brick
import os, git
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
    """get the local bb from the current working directory"""
    try:
      repo = git.Repo(path, search_parent_directories=True)
      path = Path(repo.git.working_dir)
      if not (path / ".bb").exists():
        return None
      return LocalBB(path)
    except:
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

  
  def install_dependencies(self):
    """install all dependencies"""
    for brick in self.get_depencies():
      brick.install()
  