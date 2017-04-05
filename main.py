# coding: utf-8
import os
import ezdxf
import copy
import collections
from shapely.geometry import Polygon, Point, LinearRing, box, MultiPoint, MultiPolygon
import from_dxf_to_image
import time

area = collections.namedtuple('area', 'type total living windows')
G1 = area(type='G1', total=[340000, 400000], living=[140000, 180000], windows=2)
G2 = area(type='G2', total=[490000, 590000], living=[260000, 340000], windows=3)
G3 = area(type='G3', total=[590000, 750000], living=[360000, 480000], windows=4)
G4 = area(type='G4', total=[700000, 1000000], living=[460000, 710000], windows=5)

# G1 = area(type='G1', total=[34, 40], living=[14, 18], windows=2)
# G2 = area(type='G2', total=[49, 59], living=[26, 34], windows=3)
# G3 = area(type='G3', total=[59, 75], living=[36, 48], windows=4)
# G4 = area(type='G4', total=[70, 88], living=[46, 62], windows=5)

def sortByArea(inputStr):
        return inputStr.area

def sortByCoefficient(inputStr):
        return inputStr.living[1]/inputStr.total[1]

class Region:
    currentNumber = 0
    def __init__(self, pointlist):
        self.name = Region.currentNumber
        self.poly = Polygon([[p[0], p[1]] for p in pointlist])
        self.area = self.poly.area
        self.ring = LinearRing([[p[0], p[1]] for p in pointlist])
        self.windows_num, self.windows_coord = self.windows()
        self.wae = self.ring.intersection(ring_evacuation_zone)
        Region.currentNumber += 1

    def windows(self):
        count = 0
        coordinates = []
        for i in start_points:
            point = Point(i[0], i[1])
            x = self.ring.intersection(point)
            if x:
                coordinates.append(x.coords[0])
                count += 1
        return count, coordinates

class LA:
    def __init__(self, type, total, living, form, windows):
        self.type = type
        self.total = total
        self.living = living
        self.tabu = collections.deque(maxlen=500)
        self.form = form
        self.windows = windows
        self.OK_line = Point()
        self.NO_line = Point()

# Жадным методом с учетом доп требований определяет какой надор ЛО явдяется аналитически оптимальным
def greedy_algorithm(region, working_set):
    #working_set.sort(key=sortByCoefficient, reverse=True)
    MAXWT = region.area
    MAXWIND = region.windows_num
    wt = 0
    val = 0
    wind = 0
    bagged = []
    for j in working_set[:]:
        portion = min(MAXWT - wt, j.total[1])
        if portion < j.total[0]:
            continue
        wind += j.windows
        if wind > MAXWIND:
            continue
        wt += portion
        addval  = portion * j.living[1]/j.total[1]
        val += addval
        bagged += [(j.type, portion, addval, j.windows)]
        working_set.remove(j)
        if wt >= MAXWT:
            break
    return bagged, working_set

# Заносит ЛО в ЗО основываясь на maxy или miny (зависит от верхнего или нижнего нахождения ЗО)
def LA_generation(la, region, num_la, eng_line):
    #Первый заносимый объект (линия зоны эвакуации еще ничем не занята)
        #Низ
    if region.wae.bounds[-1] == region.ring.bounds[-1]:
        try:
            first_point = [j for i in eng_line for j in list(i.coords)
                            if j[1] == eng_line.bounds[-1]]
        except TypeError:
            first_point = [i for i in eng_line.coords if i[1] == eng_line.bounds[-1]]
        second_point_y = region.ring.bounds[1]
        second_point_x = first_point[0][0] - la[1] / (first_point[0][1] - second_point_y)
        form = box(first_point[0][0], first_point[0][1], second_point_x, second_point_y)
        #Верх
    elif region.wae.bounds[1] == region.ring.bounds[1]:
        try:
            first_point = [j for i in eng_line for j in list(i.coords)
                            if j[1] == eng_line.bounds[1]]
        except TypeError:
            first_point = [i for i in eng_line.coords if i[1] == eng_line.bounds[1]]
        second_point_y = region.ring.bounds[-1]
        second_point_x = first_point[0][0] + la[1] / (first_point[0][1] - second_point_y)
        form = box(first_point[0][0], first_point[0][1], second_point_x, second_point_y)
    la = LA(la[0], la[1], la[2], form, la[3])
    return la

#Проверяет ЛО на соответсвие всем доп. требованиям размещения (непересечение ЗО, касание ЗЭ, кол-во оконных проемов)
def test_conditions(la_form, region, la_windows):
    contain = True if region.poly.contains(la_form) else False
    ezone_touch = True if la_form.intersection(region.wae).length >= 1 else False
    try:
        windows_num = True if len(la_form.intersection(MultiPoint(region.windows_coord))) >= la_windows else False
    except TypeError:
        windows_num = True if len(la_form.intersection(MultiPoint(region.windows_coord)).coords[:]) >= la_windows else False
    return(contain, ezone_touch, windows_num)

# Движение вдоль линии эвакуации на step
def shift(la, region, ezone_line, NO_line, step=5):
    cor_step = 0.0001
    points = list(la.form.bounds)
    #Вниз на 0.0001 ТРЕБУЕТ КОРРЕКТИРОВКИ!!!!!!!!!!!!!!!!!!!!!!!!!
    if box(points[0], points[1] - step, points[2], points[3] - step).bounds not in la.tabu and \
        box(points[0], points[1] - step, points[2], points[3] - step).intersection(ezone_line) and \
        type(box(points[0], points[1] - step, points[2], points[3] - step).intersection(NO_line)) == Point:
        midle_ens = box(points[0], points[1] - step, points[2], points[3] - step)
        while not region.poly.contains(midle_ens):
            points = midle_ens.bounds
            midle_ens = box(points[0], points[1] + cor_step, points[2], points[3] + cor_step)
        return midle_ens
    #Вверх на 0.0001 ТРЕБУЕТ КОРРЕКТИРОВКИ!!!!!!!!!!!!!!!!!!!!!!!!!
    elif box(points[0], points[1] + step, points[2], points[3] + step).bounds not in la.tabu and \
        box(points[0], points[1] + step, points[2], points[3] + step).intersection(ezone_line) and \
        type(box(points[0], points[1] + step, points[2], points[3] + step).intersection(NO_line)) == Point:
        midle_ens = box(points[0], points[1] - step, points[2], points[3] - step)
        while not region.poly.contains(midle_ens):
            points = midle_ens.bounds
            midle_ens = box(points[0], points[1] - cor_step, points[2], points[3] - cor_step)
        return midle_ens
    #Вправо на 0.0001 ТРЕБУЕТ КОРРЕКТИРОВКИ!!!!!!!!!!!!!!!!!!!!!!!!!
    elif box(points[0] + step, points[1], points[2] + step, points[3]).bounds not in la.tabu and \
        box(points[0] + step, points[1], points[2] + step, points[3]).intersection(ezone_line) and \
        type(box(points[0] + step, points[1], points[2] + step, points[3]).intersection(NO_line)) == Point:
        midle_ens = box(points[0] + step, points[1], points[2] + step, points[3])
        while not region.poly.contains(midle_ens):
            points = midle_ens.bounds
            midle_ens = box(points[0] - cor_step, points[1], points[2] - cor_step, points[3])
        return midle_ens
    #Влево на 0.0001 ТРЕБУЕТ КОРРЕКТИРОВКИ!!!!!!!!!!!!!!!!!!!!!!!!!
    elif box(points[0] - step, points[1], points[2] - step, points[3]).bounds not in la.tabu and \
        box(points[0] - step, points[1], points[2] - step, points[3]).intersection(ezone_line) and \
        type(box(points[0] - step, points[1], points[2] - step, points[3]).intersection(NO_line)) == Point:
        midle_ens = box(points[0] - step, points[1], points[2] - step, points[3])
        while not region.poly.contains(midle_ens):
            points = midle_ens.bounds
            midle_ens = box(points[0] + cor_step, points[1], points[2] + cor_step, points[3])
        return midle_ens
    else:
        return 0

# Меняет метрические характеристики ЛО
def change_metric(la, region):
    points = list(la.form.bounds)
    pointsZO = list(region.ring.bounds)
    # Ищем какая из точек ЛО касается линии эвакуации
    # Нижняя
    if Point(points[0], points[1]).intersection(region.wae) or Point(points[2], points[1]).intersection(region.wae):
        # Поочередно пытаемя расширить ЛО до каждой из наружных стен ЗО
        if box(points[2] - la.total / abs(points[3] - points[1]), points[1], points[2], pointsZO[3]).bounds not in la.tabu:
            return box(points[2] - la.total / abs(pointsZO[3] - points[1]), points[1], points[2], pointsZO[3])
        elif box(points[0], points[1], pointsZO[0], points[1] + la.total / abs(points[0] - pointsZO[0])).bounds not in la.tabu:
            return box(points[0], points[1], pointsZO[0], points[1] + la.total / abs(points[0] - pointsZO[0]))
        else:
            return 0
    # Верхняя
    elif Point(points[2], points[3]).intersection(region.wae) or Point(points[0], points[3]).intersection(region.wae):
        # Поочередно пытаемя расширить ЛО до каждой из наружных стен ЗО
        if box(pointsZO[0], points[3] - la.total / abs(points[2] - pointsZO[0]), points[2], points[3]).bounds not in la.tabu:
            return box(pointsZO[0], points[3] - la.total / abs(points[2] - pointsZO[0]), points[2], points[3])
        elif box(points[2] - la.total / abs(points[3] - pointsZO[1]), pointsZO[1], points[2], points[3]).bounds not in la.tabu:
            return box(points[2] - la.total / abs(points[3] - pointsZO[1]), pointsZO[1], points[2], points[3])
        else:
            return 0
    else:
        print(region.poly.contains(la.form))

#Меняем координаты на новые, удовлетворяющие всем доп. условиям. Старые координаты добаляются в tabu
def change_coord(la, region, ezone_line, NO_line, tabu_shift=False):
    # Сразу добаляем текущие параметры ЛО в tabu
    if tabu_shift:
        bufer_la_tabu = copy.copy(la.tabu)

    la.tabu.append(la.form.bounds)
    while True:
        # Изменяем метрические характеристики ЛО
        new_la = change_metric(la, region)
        # Если изменения произошли и прошли проверку, то вносим соответствующие изменения в форму ЛО и возвращаем 1
        if new_la != 0 and test_conditions(new_la, region, la.windows).count(True) == 3:
            la.form = new_la
            return 1
        # Если изменения не произошли
        elif new_la == 0:
            # Выполняем сдвиг
            #print('START shift with ezone_line = {} and NO_line = {}'.format(ezone_line, NO_line))
            new_la = shift(la, region, ezone_line, NO_line)
            #if new_la == 0:
             #   print(0)
            #else:
              #  print(list(new_la.exterior.coords))
            #print('shift', new_la)
            if new_la != 0 and test_conditions(new_la, region, la.windows).count(True) == 3:
                la.form = new_la
                return 1
            # Если сдвиг не произошел возвращаем 0
            elif new_la == 0:
                return 0
            # Если сдвиг произошел, но не прошел проверку, вносим соответствующие изменения в форму ЛО, надеясь, что
            # изменение метр. характеристик поправит ситуацию
            else:
                la.form = new_la
        # Если изменения метр. характеристик произошли, но не прошли проверку, то добаляем текущие параметры ЛО в tabu
        else:
            la.tabu.append(new_la.bounds)

    if tabu_shift:
        la.tabu = bufer_la_tabu

# Завершающий этап разбиения ЗО, на котором происходит объединение размещенных ЛО и смежных с ними вакантныйх областей.
def union_zones(zones_list, region):
    working_zones_list = copy.copy(zones_list[::-1])
    end_zones_dict = {}
    end_zones_list = []

    BaseMultiPoly = zones_list[0].form
    for i in zones_list:
        BaseMultiPoly = BaseMultiPoly.union(i.form)
    DifferPoly = region.poly.difference(BaseMultiPoly)

    for h in range(len(working_zones_list)):
        MultiPoly = copy.copy(BaseMultiPoly)
        for i in working_zones_list[:-1]:
            MultiPoly = MultiPoly.difference(i.form)
        end_zones_dict[working_zones_list[-1]] = MultiPoly
        end_zones_list.append(MultiPoly)
        BaseMultiPoly = BaseMultiPoly.difference(MultiPoly)
        working_zones_list.pop()

    for i in end_zones_dict:
        # if type(DifferPoly) != 'shapely.geometry.polygon.Polygon':
        #     for j in DifferPoly:
        #         print(type(j))
        #         if end_zones_dict[i].touches(j):
        #             end_zones_dict[i] = end_zones_dict[i].union(j)
        if end_zones_dict[i].touches(DifferPoly):
                end_zones_dict[i] = end_zones_dict[i].union(DifferPoly)

    for i in range(len(end_zones_list)):
        # for j in DifferPoly:
        if end_zones_list[i].touches(DifferPoly):
            end_zones_list[i] = end_zones_list[i].union(DifferPoly)

    for itom in range(len(end_zones_list)):
        if round(end_zones_list[itom].area, 5)!= round(zones_list[itom].form.area, 5):
            return 0

    return end_zones_list

#Запускает основную процедуру разделения ЗО
def partition(regions, working_set):
    change_working_set = working_set
    f = {}
    end = {}
    for i in regions:
        local_area_set, change_working_set = greedy_algorithm(i, change_working_set)
        f[i] = local_area_set
    for i in f:
        k = 0
        # Линия эвакуации, вдоль которой нужно двигать ЛО
        OK_line = i.wae

        # Линия эвакуации, которой нельзя касаться
        NO_line = Point()

        for j in f[i]:
            la = LA_generation(j, i, k, OK_line)
            la.OK_line = OK_line
            la.NO_line = NO_line
            if test_conditions(la.form, i, la.windows).count(True) != 3:
                #print(list(la.form.exterior.coords))
                #print('START change_coord')
                change_coord(la, i, OK_line, NO_line)
                #print(list(la.form.exterior.coords))
            if i not in end:
                end[i] = [la]
            else:
                end[i].append(la)
            k += 1
            OK_line = OK_line.difference(la.form)
            NO_line = NO_line.union(i.wae.difference(OK_line))

        # Выполняется процедура объединения областей внутри ЗО до состояния плотной упаковуи
        # (возвращает 0 или конечный результат для печати)
        for h in range(1500):
            union_ens = union_zones(end[i], i)
            if not union_ens:
                start_len = len(end[i])
                temporary_list = []
                while True:
                    working_LO = end[i].pop()
                    new_LO = change_coord(working_LO, i, working_LO.OK_line, working_LO.NO_line, tabu_shift=True)
                    if new_LO:
                        end[i].append(working_LO)
                        if len(temporary_list) != 0:
                            end[i].append(temporary_list.pop())
                    else:
                        temporary_list.append(working_LO)
                    if len(end[i]) == 0:
                        return 0
                    elif len(end[i]) == start_len:
                        break
            else:
                end[i] = union_ens
                break
    #ezone_line = la.form.intersection(regions[1].wae)
    return end

# Функция генерирует список координат специальных точек (оконных проемов) на границе ЗО
def start_points_func(windows):
    start_points = []
    for e in windows:
        start_points.append(e.dxf.start)
    return start_points

def main(file = "drawing1.dxf", k1 = 3, k2 = 3, k3 = 1, k4 = 1):
    _time = time.time()
    global working_set
    global start_points
    global ring_evacuation_zone

    working_set = []
    for i in range(k4): working_set.append(G4)
    for i in range(k3): working_set.append(G3)
    for i in range(k2): working_set.append(G2)
    for i in range(k1): working_set.append(G1)
    dwg = ezdxf.readfile(file)
    msp = dwg.modelspace()

    __regions = msp.query('LWPOLYLINE[color==1]')
    __evacuation_zone = msp.query('LWPOLYLINE[color==3]')
    windows = msp.query('LINE[color==2]')
    #exterior_walls = msp.query('LINE[color==256]')
    evacuation_zone = [p[:2] for p in __evacuation_zone[0]]
    ring_evacuation_zone = LinearRing([[p[0], p[1]] for p in evacuation_zone])

    start_points = start_points_func(windows)
    regions = []
    for i in __regions:
        pointlist = [h[:2] for h in i]
        regions.append(Region(pointlist))

    regions.sort(key=sortByArea)

    d = {}

    for i in regions[:]:
        for j in working_set:
            if j.total[0] <= i.area <= j.total[1] and i.windows_num >= j.windows:
                d[i] = [i.poly] #[(j.type, i.area, i.area*j.living[1]/j.total[1])]
                regions.remove(i)
                working_set.remove(j)
                break

    f = partition(regions, working_set)
    #print(d)
    #print(f)
    d.update(f)

    for i in d:
        for j in d[i]:
            try:
                arg = j.form.bounds
                msp.add_lwpolyline(list(j.form.exterior.coords))
                msp.add_text(str(round(j.total/10000, 2))).set_pos((arg[0],arg[1]), align='BOTTOM_LEFT')
            except:
                arg = j.bounds
                msp.add_lwpolyline(list(j.exterior.coords))
                msp.add_text(str(round(j.area/10000, 2))).set_pos((arg[0],arg[1]), align='BOTTOM_LEFT')
    dwg.saveas("temp_file.dxf")
    from_dxf_to_image.main_def("temp_file.dxf")
    os.remove("temp_file.dxf")
    print(time.time() - _time)
    return

#if __name__ == '__main__':
main()


#d.update(f)
#print(d)
#print(partition)
#for i in range(len(regions)):
 #   for j in range(len(start_points_windows)):
  #      regions[i]
#print(count)
#line = msp.query('LWPOLYLINE')[0]
#print(line.color)
#with lines.points() as points:
 #   print(poly_area(points))
#modelspace.add_line((0, 0), (10, 0), dxfattribs={'color': 7})
#drawing.layers.create('TEXTLAYER', dxfattribs={'color': 2})
#modelspace.add_text('Test', dxfattribs={'insert': (0, 0.2), 'layer': 'TEXTLAYER'})
#drawing.saveas('test.dxf')