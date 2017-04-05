import ezdxf
import collections
from shapely.geometry import box, LineString, MultiLineString, MultiPoint, Point
b = box(4.0, 0.0, 0.0, 4.0)
c = box(0.0, 0.0, 4.0, 4.0)
d = box(0.0, 2.0, 4.0, 4.0)
listok = [c.bounds, d.bounds]
l = LineString([(0, 0), (0, 1)])
ML = MultiLineString([((2, 4), (2, 0)), ((2, 0), (6, 0)), ((6, 0), (6, 6))])
MP = MultiPoint([(0.0, 0.0), (0.0, 1.0), (3.0, 3.0)])
P = Point(2.0, 0.0)
dwg = ezdxf.readfile("drawing1.dxf")
msp = dwg.modelspace()
points1 = [(7952.84270346272, 4035.350000054488), (7956.8292278781555, 4035.350000054488), (7956.8292278781555, 4029.454540893406), (7960.529999879669, 4029.454540893406), (7960.529999879669, 4027.675000054499), (7952.84270346272, 4027.675000054499), (7949.999999879671, 4027.675000054499), (7949.999999879671, 4035.350000054488), (7952.84270346272, 4035.350000054488)]
points2 = [(7956.8292278781555, 4035.350000054488), (7960.529999879669, 4035.350000054488), (7963.029999845825, 4035.350000054488), (7963.029999879669, 4035.350000054488), (7963.029999879669, 4029.454540893406), (7963.029999845825, 4029.454540893406), (7960.529999879669, 4029.454540893406), (7956.8292278781555, 4029.454540893406), (7956.8292278781555, 4035.350000054488)]
points3 = [(7952.842703462733, 4027.675000054499), (7960.529999879669, 4027.675000054499), (7960.529999879669, 4025.895459215578), (7956.829227878132, 4025.895459215578), (7956.829227878132, 4020.000000054497), (7952.842703462733, 4020.000000054497), (7949.999999879671, 4020.000000054497), (7949.999999879671, 4027.675000054499), (7952.842703462733, 4027.675000054499)]
points4 = [(7960.529999879669, 4025.895459215578), (7963.029999845825, 4025.895459215578), (7963.029999879669, 4025.895459215578), (7963.029999879669, 4020.000000054497), (7963.029999845825, 4020.000000054497), (7960.529999879669, 4020.000000054497), (7956.829227878132, 4020.000000054497), (7956.829227878132, 4025.895459215578), (7960.529999879669, 4025.895459215578)]


msp.add_lwpolyline(points1)
msp.add_lwpolyline(points2)
msp.add_lwpolyline(points3)
msp.add_lwpolyline(points4)
dwg.saveas("lwpolyline4.dxf")
