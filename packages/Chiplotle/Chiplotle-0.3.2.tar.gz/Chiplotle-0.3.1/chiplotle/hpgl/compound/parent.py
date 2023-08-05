from chiplotle.hpgl.compound.group import Group
from chiplotle.hpgl.coordinatepair import CoordinatePair
from chiplotle.hpgl.commands import SP
from chiplotle.hpgl.compound.pen import Pen
from chiplotle.interfaces.parentage.interface import ParentageInterface
import types

class Parent(Group):
   
   _scalable = ['xy']

   def __init__(self, xy, shapes=None, pen=None):
      Group.__init__(self, xy, shapes, pen)
      self._parentage = ParentageInterface(self)

   ## PUBLIC ATTRIBUTES ##


   @property
   def parentage(self):
      return self._parentage

   @property
   def xyabsolute(self):
      if self.parentage.parent:
         return self.parentage.parent.xyabsolute + self.xy
      else:
         return self.xy

   @property
   def xabsolute(self):
      #return self._getAbsCoord(0)
      if self.parentage.parent:
         return self.parentage.parent.xabsolute + self.x
      else:
         return self.x

   @property
   def yabsolute(self):
      #return self._getAbsCoord(1)
      if self.parentage.parent:
         return self.parentage.parent.yabsolute + self.y
      else:
         return self.y
