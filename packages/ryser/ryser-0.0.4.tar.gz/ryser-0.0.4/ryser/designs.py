# Created 18th December 2010. Last updated Thu Aug  9 16:14:34 BST 2012

class Latin:

  def __init__(self, P, size):
     self._P = P
     self._size = size

  def size(self):
     return self._size

  def fixed_cells(self):
     return self._P

