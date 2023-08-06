import math
import svgwrite
from svgwrite import rgb
#
# http://www.w3.org/TR/SVG11/types.html#ColorKeywords
# Note both grey and gray are valide but only color not colour is valid.
# http://www.w3.org/TR/SVG11/struct.html#Head
# http://www.w3.org/TR/SVG11/struct.html#UseElement
# http://commons.oreilly.com/wiki/index.php/SVG_Essentials/Document_Structure#svgess-CHP-4-EX-7
# TODO change defs to symbol. Put in preserveAspectRatio="xMidYMid slice" viewBox="0 0 40 40"
#      http://commons.oreilly.com/wiki/index.php/SVG_Essentials
# http://www.w3.org/1999/06/25/WD-SVG-19990625/coords.html#EstablishingANewViewport preserveaspectratio
#
progname = 'defs_test'


def create_svg(name):
    svg_size_width = 900
    svg_size_height = 900
    font_size = 20
    triangle_size = 50
    title1 = name + ': Example of creating your own colors and defs/use.'
    sample = (
            )
    dwg = svgwrite.Drawing(name, (svg_size_width, svg_size_height), debug=True)
    # http://www.w3.org/TR/SVG11/struct.html#Head
    # "sometimes it is desired to define a graphical object and prevent it from being directly
    # rendered. it is only there to be referenced elsewhere. To do this, and to allow convenient
    # grouping defined content, SVG provides the 'defs' element."
    #

    # 1. create template polygons
    triangle_points = [
        (triangle_size/-2.0, triangle_size/-2.0),
        (triangle_size/2.0, triangle_size/-2.0),
        (0, (triangle_size * math.sqrt(3.0) / 4.0))
    ]
    # viewport of symbols starts a (0,0), so define a appropriate viewport
    # or just shift coordinates, simpler
    shift = triangle_size/2
    polygon_points = [(point[0]+shift, point[1]+shift) for point in triangle_points]

    polygon_without_fill =dwg.polygon(polygon_points, stroke='none')
    polygon_with_fill = dwg.polygon(polygon_points, stroke='none')

    # 2. create the symbols
    symbol_without_fill = dwg.g(id='symbol_without_fill')
    symbol_with_fill = dwg.g(id='symbol_with_fill', fill='black')

    # to set viewport: (to avoid shifting coordinates)
    # symbol_without_fill.viewbox(minx, miny, maxx, maxy) ... I tried
    # viewbox(-shift, +shift, -shift, +shift) and got just big triangles,
    # so I stuck to coordinate-shifting ;-)

    # 3. add triangles to the symbol containers
    symbol_without_fill.add(polygon_without_fill)
    symbol_with_fill.add(polygon_with_fill)

    # 4. add symbols to the defs section
    dwg.defs.add(symbol_without_fill)
    dwg.defs.add(symbol_with_fill)

    # Background will be dark but not black so the background does not overwhelm the colors.
    dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), rx=None, ry=None, fill='grey'))
    # Give the name of the example and a title.
    y = font_size + 5
    # The color will show because there is no color listed in the defs. 
    dwg.add(dwg.text(title1, insert=(0, y),
            font_family="serif", font_size=font_size, fill='white'))
    y += font_size
    #
    tri_created1 = dwg.use(symbol_without_fill, insert=(200, 200), fill='yellow')
    dwg.add(tri_created1)
    # Color not overridden when color is specified in the defs.
    tri_created2 = dwg.use(href='#symbol_with_fill', insert=(300, 300), fill=rgb(0, 0, 200))
    dwg.add(tri_created2)
    # Not only is color not overridden but size is not overridden also!
    tri_created3 = dwg.use(href='#symbol_with_fill', insert=(400, 400), size=(300,300), fill=rgb(200, 0, 0))
    dwg.add(tri_created3)

    # but size can be changed be transfomation, but ALL coordinates will be
    # transformed, also the insert point! 250 -> 500
    # I repeat, I am not a SVG-Expert!!!!
    tri_created4 = dwg.use(href='#symbol_with_fill', insert=(250, 250), fill=rgb(200, 0, 0))
    # using the Transform mixin method scale()
    tri_created4.scale(2)
    dwg.add(tri_created4)

    #
    dwg.save()


if __name__ == '__main__':
    create_svg(progname + '.svg')

# vim: expandtab shiftwidth=4 tabstop=8 softtabstop=4 textwidth=99


