import codecs

READ_SIZE = 20000

class Reader(object):
    def __init__(self,filename, seek=0):
        self.filename = filename
        self.fh = codecs.open(filename,'r','utf-8')
        if seek:
            self.fh.seek(seek)
        self.open_line = []
        self.open_ceil = None
    
    def tell(self):
        return self.fh.tell()

    def import_all(self):
        while self.parse_next_block():
            pass
        self.write_open_line()

    def read_next_block(self):
        data = self.fh.read(READ_SIZE)
        if not data:return
        while data[-1]  in ('"',',','\n'):
            next_read = self.fh.read(1)
            if not next_read:
                break
            data += next_read
        return data
    
    def parse_next_block(self):
        data = self.read_next_block() 
        if not data:
            return False
        lines = data.split('\n')
        first_line = True
        for line in lines:
            if first_line:
                first_line = False
            else:
                if self.open_ceil:
                    self.add_to_open_ceil('\n')

            if self.start_as_new(line):
                self.write_open_line()
            pieces = line.split(',')
            first_piece = True
            for piece in pieces:
                if self.start_as_new(piece):# piece[0] == '"' and piece[1]!='"':
                    self.finish_open_ceil()
                    self.add_to_open_ceil(piece[1:])
                else:
                    if not first_piece:
                        self.add_to_open_ceil(',')
                    self.add_to_open_ceil(piece)

                if first_piece:
                    first_piece = False
        return True

    def start_as_new(self,piece):
        if not piece.startswith('"'):
            return False
        len_char = 1
        for char in piece[1:]:
            if char == '"':
                len_char += 1
            else:
                break

        return len_char % 2

    def add_to_open_ceil(self,piece):
        piece = piece.replace('""','"')
        self.open_ceil =  self.open_ceil + piece if self.open_ceil else piece

    def finish_open_ceil(self):
        if self.open_ceil is None:
            return
        self.open_line.append(self.open_ceil)
        self.open_ceil = None

    def write_open_line(self):
        self.finish_open_ceil()
        if not self.open_line:
            return 
        if len(self.open_line) == 1 and self.open_line[0]=='':
            #first empty line
            self.open_line = []
            return
        self.write_row(self.open_line)
        self.open_line = []

    def write_row(self,row):
        raise ImplementationError('Write row must be overriden')

