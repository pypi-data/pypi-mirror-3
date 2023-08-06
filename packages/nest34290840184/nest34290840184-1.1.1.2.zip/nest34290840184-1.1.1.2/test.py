
"""''' hello '''"""
def pr( e ):
    if isinstance( e, list ) :
        for e1 in e :
            pr( e1 )
    else :
        print( e )


movies = ["a",
    "b", 4]

expand = [['ooo','pp']]

movies.extend(expand)

movies.insert( 2, 90 )

pr(movies)
