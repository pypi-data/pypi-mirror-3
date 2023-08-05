class Request(object):
    pass

request = Request()
setattr(request, 'args', {})


q1 = build_inner_query(request, [('Metadata/Location/Building', 'Etcheverry Hall')])[0][:-9]
q2 = build_inner_query(request, [('Metadata/Location/Building', 'Barker')])[0][:-9]
q3 = build_inner_query(request, [('Metadata/Location/Building', 'Evans Hall')])[0][:-9]
q4 = build_inner_query(request, [('Properties/UnitofMeasure', 'kW')])[0][:-9]

SIMPLEQ = """
(
 (SELECT stream_id FROM metadata2 m WHERE (tagname = 'Metadata/Location/Building' AND tagval = 'Etcheverry Hall'))
UNION
 (SELECT stream_id FROM metadata2 m WHERE (tagname = 'Metadata/Location/Building' AND tagval = 'Barker'))
UNION
 (SELECT stream_id FROM metadata2 m WHERE (tagname = 'Metadata/Location/Building' AND tagval = 'Evans Hall'))
)
INTERSECT
 (SELECT stream_id FROM metadata2 m WHERE (tagname = 'Properties/UnitofMeasure' AND tagval = 'kW'))
"""

SIMPLEQ = """
(
 (SELECT stream_id FROM metadata2 m)
)
EXCEPT
 (SELECT stream_id FROM metadata2 m WHERE (tagname = 'Properties/UnitofMeasure' AND tagval = 'kW'))
"""

# connection = pgdb.connect(host="jackalope.cs.berkeley.edu",
#                           user="ar",
#                           password="password",
#                           database="archiver")
# cur = connection.cursor()
# q = '(' + q1[:-9] + ' UNION ' + q2[:-9] + ' UNION ' + q3[:-9] + ') INTERSECT' + q4[:-9]
# start = time.time()
# cur.execute(q)
# match = cur.fetchall()
# print time.time() - start
# print match
# print q
# print '=' * 50


# ast = AndOperator(set([Clause('c1'), Clause('c2'), NotOperator([Clause('c3')]), NotOperator([Clause('c4')])]))
# print ast
# print ast.render()

# ast = AndOperator([OrOperator([Clause('c1'), Clause('c2')]), NotOperator(Clause('c3'))])
# print ast
# print ast.render()


ast = AndOperator([Clause('c2'), OrOperator([Clause('c1'), NotOperator(Clause('c3'))])])
print ast
print normalize(ast).render()
# print ast.render()

# ast = AndOperator([Clause('c2'), OrOperator([Clause('c1'), NotOperator(Clause('c3'))])])
# print ast
# print ast.render()

# ast = AndOperator([OrOperator([Clause(q1), Clause(q2), Clause(q3)])]) # , NotOperator(Clause(q4))])
# print ast.render()

#start = time.time()
# cur.execute(ast.render())
#match = cur.fetchall()
#print match
#print time.time() - start

# cur.close()
# connection.close()
