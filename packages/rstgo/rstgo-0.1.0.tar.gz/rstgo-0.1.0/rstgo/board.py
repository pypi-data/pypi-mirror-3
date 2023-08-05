from itertools import cycle
import os

from PIL import Image


class TileSet(object):

    def __init__(self, name='tiny'):
        self.name = name
        self.tile_size = (14, 14)
        self.resource_dir = '%s/resources/%s' % (os.path.dirname(__file__), name)
           
        self.tile_cache = {}
        self.valid_tiles = [
            'tl-corner', 'tr-corner', 'bl-corner', 'br-corner',
            't-side', 'b-side', 'l-side', 'r-side',
            'point', 'starpoint', 'empty',
            'black', 'white',
        ]

    def __getitem__(self, tile):
        if tile not in self.valid_tiles:
            raise KeyError
        if tile not in self.tile_cache:
            self.tile_cache[tile] = Image.open('%s/%s.png' % (self.resource_dir, tile))
        return self.tile_cache[tile]

    def annotate(self, tile, annotation):
        translations = {
            'triangle': u'\u25be',
            'square': u'\u25aa',
            'bullet': u'\u2022',
        }
        annotation = translations.get(annotation, str(annotation))
        annotated_tile_name = '-'.join([tile, annotation])
        if annotated_tile_name not in self.tile_cache:
            tile_object = self[tile].copy()
            self.tile_cache[annotated_tile_name] = tile_object
        return self.tile_cache[annotated_tile_name]
      
    def render(self, diagram):
        image = Image.new('RGBA', 
            (diagram.board.size[0] * self.tile_size[0], 
             diagram.board.size[1] * self.tile_size[1])
        )
        for x in xrange(diagram.board.size[0]):
            for y in xrange(diagram.board.size[1]):
        	point = x, y
                if point in diagram.initial_black:
                    tile = 'black'
                elif point in diagram.initial_white:
                    tile = 'white'
                
                elif diagram.board.left_edge and x == 0:
                    if diagram.board.top_edge and y == 0:
                       tile = 'tl-corner'
                    elif diagram.board.bottom_edge and y == diagram.board.size[1] - 1:
                       tile = 'bl-corner'
                    else:
                       tile = 'l-side'
                elif diagram.board.right_edge and x == diagram.board.size[0] - 1:
                    if diagram.board.top_edge and y == 0:
                       tile = 'tr-corner'
                    elif diagram.board.bottom_edge and y == diagram.board.size[1] - 1:
                       tile = 'br-corner'
                    else:
                       tile = 'r-side'
                elif diagram.board.top_edge and y == 0:
                    tile='t-side'
                elif diagram.board.bottom_edge and y == diagram.board.size[1] - 1:
                    tile='b-side'
                elif (x, y) in diagram.board.star_points:
                    tile = 'starpoint'
                else:
                    tile = 'point'
                box = (x*self.tile_size[0], y*self.tile_size[1],
                       (x+1)*self.tile_size[0], (y+1)*self.tile_size[1])
                image.paste(self[tile], box)

        for i in diagram.sequence:
            if i % 2:
                player = diagram.first
            else:
        	player = diagram.second
            x, y = move
            box = (x*self.tile_size[0], y*self.tile_size[1],
                   (x+1)*self.tile_size[0], (y+1)*self.tile_size[1])
            tile = self.annotate(self[player], i)
            image.paste(tile, box)
        return image


class Board(object):

    def __init__(self, size=(19, 19), left_edge=True, right_edge=True, top_edge=True, bottom_edge=True):
        self.size=size
        self.top_edge = top_edge
        self.left_edge = left_edge
        self.right_edge = right_edge
        self.bottom_edge = bottom_edge
        self.set_star_points() 
        
    def set_star_points(self):
        x_ranks = set()
        y_ranks = set()
        if self.left_edge and not self.right_edge:
            if self.size[0] >= 4:
                x_ranks.add(3)
            if self.size[0] >= 10:
                x_ranks.add(9)
            if self.size[0] >= 16:
                x_ranks.add(15)

        elif self.right_edge and not self.left_edge:
            if self.size[0] >= 4:
                x_ranks.add(self.size[0] - 4)
            if self.size[0] >= 10:
                x_ranks.add(self.size[0] - 10)
            if self.size[0] >= 16:
                x_ranks.add(self.size[0] - 16)
            
        elif self.left_edge and self.right_edge:
            if self.size[0] >=9:
                x_ranks.add(3)
                x_ranks.add(self.size[0] - 4)
            if self.size[0] % 2 and self.size[0] >= 15:
                x_ranks.add((self.size[0] - 1) // 2)

        if self.top_edge and not self.bottom_edge:
            if self.size[1] >= 4:
                y_ranks.add(3)
            if self.size[1] >= 10:
                y_ranks.add(9)
            if self.size[1] >= 16:
                y_ranks.add(15)
 
        elif not self.top_edge and self.bottom_edge:
            if self.size[1] >= 4:
                y_ranks.add(self.size[1] - 4)
            if self.size[1] >= 10:
                y_ranks.add(self.size[1] - 10)
            if self.size[1] >= 16:
                y_ranks.add(self.size[1] - 16)

        elif self.top_edge and self.bottom_edge:
            if self.size[1] >=9:
                y_ranks.add(3)
                y_ranks.add(self.size[1] - 4)
            if self.size[1] % 2 and self.size[1] >= 15:
                y_ranks.add((self.size[1] - 1) // 2)
    
        self.star_points = set()
        for x in x_ranks:
            for y in y_ranks:
                self.star_points.add((x, y))


class GoDiagram(object):

    @classmethod
    def load_diagram_from_parser(cls, parser):
        board = Board(
            size=parser.board_size(),
            top_edge=parser.top_edge,
            left_edge=parser.left_edge,
            right_edge=parser.right_edge,
            bottom_edge=parser.bottom_edge,
        )
        return cls(board=board,
            initial_black = parser.initial_black,
            initial_white = parser.initial_white,
            sequence = parser.sequence_moves,
        )

    def __init__(self, board=Board(), initial_black=None, initial_white=None, sequence=None, first='black'):
        self.board = board
        self.initial_black = initial_black or set()
        self.initial_white = initial_white or set()
        self.sequence = sequence or {}
        self.first = first
        if self.first == 'black':
            self.second = 'white'
        elif self.first == 'white':
            self.second = 'black'
        else:
            self.first = 'black'
            self.second = 'white'
        self.tiles = TileSet('tiny')

    def render(self):
        self.image = self.tiles.render(self)

    def show(self):
        self.image.show()

    def save(self, filename, format):
        self.image.save(filename, format)
        
if __name__ == '__main__':
    black_set = set([(4, 4), (4, 5)])
    white_set = set([(3, 2), (7, 3), (8, 3)])
    sequence = {1: (2, 2), 2: (1,2), 3: (2,3), 4: (3,1)}
    
    board = Board(
        (9, 9), 
    )
    Diagram(board=board, 
            initial_black=black_set, 
            initial_white=white_set, 
            sequence=sequence).draw()
