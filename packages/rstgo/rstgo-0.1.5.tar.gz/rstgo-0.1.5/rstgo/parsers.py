
class MalformedGoDiagram(ValueError): 
    pass

class GoDiagramParser(object):
    def __init__(self):
        self.line_prefix = ''
        self.top_edge = False
        self.left_edge = False
        self.right_edge = False
        self.bottom_edge = False
        self.board_width = 0
        self.board_height = 0
        self.initial_black = set()
        self.initial_white = set()
        self.sequence_moves = {}
        self.annotated_moves = {}
        self.board_parsed = False

    def board_size(self):
        return self.board_width, self.board_height

    def parse(self, board):
        board = iter(board)
        self.parse_header(board.next())
        for line in board:
            if not self.board_parsed:
                self.parse_board(line)
            else: 
                self.parse_footer(line)

    def parse_header(self, line):
        line = line.strip()
        if line.startswith('$$'):
            self.line_prefix = '$$'
        if '---' in line:
            line = line[len(self.line_prefix):]
            line = line.strip()
            # top border:
            if any(c != '-' for c in line):
                raise MalformedGoDiagram('Top edge must consist of only "-" characters')
            self.top_edge=True
        else:
            self.parse_board(line)
                
    def parse_board(self, line):
        line = line.strip()
        if not line.startswith(self.line_prefix):
            raise MalformedGoDiagram("All lines must start with $$ if any lines start with $$")
        line = line[len(self.line_prefix):]
        line = line.strip()
        if '---' in line:
            self.board_parsed = True
            self.parse_footer(line)
        else:
            self.board_height += 1
            if line[0] == '|':
                self.left_edge = True
                line = line[1:]
            if line[-1] == '|':
                self.right_edge = True
                line = line[:-1]
            points = line.split()
            if not self.board_width:
                self.board_width = len(points)
            elif self.board_width != len(points):
                raise MalformedGoDiagram("All lines must be the same length")
            for i, point in enumerate(points):
                coord = (i, self.board_height - 1)
                if point == 'X':
                    self.initial_black.add(coord)
                elif point == 'O':
                    self.initial_white.add(coord)
                elif point in list('1234567890'):
                    self.sequence_moves[int(point)] = coord
                elif point in list('abcdefghijklmnopqrstuvwxyz'):
                    self.annotated_moves[point] = coord
                elif point in list('.,'):
                    #Empty point
                    pass
                else:
                    raise MalformedGoDiagram('Unrecognized board marking: "%s"' % point)
                    
    def parse_footer(self, line):
        if '---' in line:
            self.bottom_edge = True
            if any(c != '-' for c in line):
                raise MalformedGoDiagram('Top edge must consist of only "-" characters')
        else:
            #Not handling other footer information yet.
            pass

