
# parsetab.py
# This file is automatically generated. Do not edit.
_tabversion = '3.2'

_lr_method = 'LALR'

_lr_signature = '6\xd8\x1d\xbb\x84\xd1~\xc4\\\xe0\xc7Q\x9d\xc4t\x15'
    
_lr_action_items = {'AND':([15,16,17,20,25,26,27,28,29,30,31,],[-9,-10,23,23,23,-15,-11,-16,-17,23,23,]),'STAR':([2,],[3,]),'LIKE':([14,],[22,]),'TAGS':([4,],[9,]),'DISTINCT':([2,],[4,]),'LVALUE':([2,4,10,11,13,18,19,23,24,],[5,8,5,14,14,14,26,14,14,]),'OR':([15,16,17,20,25,26,27,28,29,30,31,],[-9,-10,24,24,24,-15,-11,-16,-17,24,24,]),'COMMA':([5,],[10,]),'QSTRING':([21,22,],[28,29,]),'LPAREN':([11,13,18,23,24,],[13,13,13,13,13,]),'NOT':([11,13,18,23,24,],[18,18,18,18,18,]),'RPAREN':([15,16,20,25,26,27,28,29,30,31,],[-9,-10,27,-14,-15,-11,-16,-17,-12,-13,]),'HAS':([11,13,18,23,24,],[19,19,19,19,19,]),'WHERE':([3,5,6,7,8,9,12,],[-4,-7,11,-3,-5,-6,-8,]),'EQ':([14,],[21,]),'SELECT':([0,],[2,]),'$end':([1,3,5,6,7,8,9,12,15,16,17,25,26,27,28,29,30,31,],[0,-4,-7,-2,-3,-5,-6,-8,-9,-10,-1,-14,-15,-11,-16,-17,-12,-13,]),}

_lr_action = { }
for _k, _v in _lr_action_items.items():
   for _x,_y in zip(_v[0],_v[1]):
      if not _x in _lr_action:  _lr_action[_x] = { }
      _lr_action[_x][_k] = _y
del _lr_action_items

_lr_goto_items = {'statement_unary':([11,13,18,23,24,],[15,15,15,15,15,]),'selector':([2,],[6,]),'statement_binary':([11,13,18,23,24,],[16,16,16,16,16,]),'statement':([11,13,18,23,24,],[17,20,25,30,31,]),'query':([0,],[1,]),'tag_list':([2,10,],[7,12,]),}

_lr_goto = { }
for _k, _v in _lr_goto_items.items():
   for _x,_y in zip(_v[0],_v[1]):
       if not _x in _lr_goto: _lr_goto[_x] = { }
       _lr_goto[_x][_k] = _y
del _lr_goto_items
_lr_productions = [
  ("S' -> query","S'",1,None,None,None),
  ('query -> SELECT selector WHERE statement','query',4,'p_query','queryparse.py',78),
  ('query -> SELECT selector','query',2,'p_query','queryparse.py',79),
  ('selector -> tag_list','selector',1,'p_selector','queryparse.py',90),
  ('selector -> STAR','selector',1,'p_selector','queryparse.py',91),
  ('selector -> DISTINCT LVALUE','selector',2,'p_selector','queryparse.py',92),
  ('selector -> DISTINCT TAGS','selector',2,'p_selector','queryparse.py',93),
  ('tag_list -> LVALUE','tag_list',1,'p_tag_list','queryparse.py',117),
  ('tag_list -> LVALUE COMMA tag_list','tag_list',3,'p_tag_list','queryparse.py',118),
  ('statement -> statement_unary','statement',1,'p_statement','queryparse.py',125),
  ('statement -> statement_binary','statement',1,'p_statement','queryparse.py',126),
  ('statement -> LPAREN statement RPAREN','statement',3,'p_statement','queryparse.py',127),
  ('statement -> statement AND statement','statement',3,'p_statement','queryparse.py',128),
  ('statement -> statement OR statement','statement',3,'p_statement','queryparse.py',129),
  ('statement -> NOT statement','statement',2,'p_statement','queryparse.py',130),
  ('statement_unary -> HAS LVALUE','statement_unary',2,'p_statement_unary','queryparse.py',144),
  ('statement_binary -> LVALUE EQ QSTRING','statement_binary',3,'p_statement_binary','queryparse.py',150),
  ('statement_binary -> LVALUE LIKE QSTRING','statement_binary',3,'p_statement_binary','queryparse.py',151),
]
