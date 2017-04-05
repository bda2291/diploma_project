rooms = ('bathroom', 'room', 'living_room', 'kitchen', 'hall')

class geometrical_object:
    def get_area(self, area_min, length_min, shape_mode):
        return {'vertical':(length_min, area_min/length_min), 'horizontal':(area_min/length_min, length_min), 'square':(area_min/2, area_min/2)}.get(shape_mode)

class bathroom(geometrical_object):
    # adjacent_with = ('kitchen')
    area_min = 4
    area_max = 4
    length_min = 1.7

    def __init__(self, x, y, shape_mode):
        self.x = x
        self.y = y
        self.a, self.b = super().get_area(bathroom.area_min, bathroom.length_min, shape_mode)

class room(geometrical_object):
    area_min = 10
    area_max = 14
    length_min = 2.3
    adjacent_with = ('window')

    def __init__(self, x, y, shape_mode):
        self.x = x
        self.y = y
        self.a, self.b = super().get_area(room.area_min, room.length_min, shape_mode)

class living_room(geometrical_object):
    area_min = 14
    area_max = 20
    length_min = 2.7
    adjacent_with = ('window')

    def __init__(self, x, y, shape_mode):
        self.x = x
        self.y = y
        self.a, self.b = super().get_area(living_room.area_min, living_room.length_min, shape_mode)

class kitchen(geometrical_object):
    area_min = 8
    area_max = 10
    length_min = 2.3
    adjacent_with = ('window')

    def __init__(self, x, y, shape_mode):
        self.x = x
        self.y = y
        self.a, self.b = super().get_area(kitchen.area_min, kitchen.length_min, shape_mode)

class hall(geometrical_object):
    area_min = 4
    area_max = 5
    length_min = 1.4
    adjacent_with = ('exit')

    def __init__(self, x, y, shape_mode):
        self.x = x
        self.y = y
        self.a, self.b = super().get_area(hall.area_min, hall.length_min, shape_mode)

# class corridor(geometrical_object):
#     length_min = 1
#     adjacent_with = ('hall')

rooms_dict = {'bathroom': bathroom, 'room': room, 'living_room': living_room, 'kitchen': kitchen, 'hall': hall}
