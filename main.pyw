from tkinter import *
from settings import settings as ss
from random import randint
from colors import COLORS

MOUSE_OFFSET = 2
CON_TEXT_WIDTH = 7
CON_HEIGHT = 12

class Debug:
    def print_flags(self):
        longest = 0 
        for flag, value in self.flags.items():
            text = f'{flag} ; {str(value)}'
            if len(text) > longest:
                longest = len(text)
            print(text)
        print('-'*longest)

class Block(Debug):

    blocks = []
    dtypes = {}

    def __init__(self, canvas: Canvas, setting: dict):
        super().__init__()
        self.flags = {
            'grabbed': None,
            'output': None,
            'input': None,
            'templine': None,
            'setting': setting,
        }
        self.canvas = canvas
        self.draw()
        Block.blocks.append(self)

    def redraw(self):
        for index, line in enumerate(self.inputLines):
            if line is not None:
                self.remove_input_line(line, index, False)
        for output in self.outputLines:
            for line in output:
                Block.remove_output_line(line)
        self.canvas.delete(self.flags['setting']['name'])
        self.draw()
        self.reassign_outputs()

    def reassign_outputs(self):
        outputs = [output for output, dtype in self.flags['setting']['outputs']]
        for index, output in enumerate(outputs):
            for block in Block.blocks:
                otherIndex = 0
                for input, dtype, inputName in block.flags['setting']['inputs']:
                    if input == output:
                        line = block.inputLines[otherIndex]
                        self.outputLines[index].append(line)
                        ox1, oy1, ox2, oy2 = self.canvas.coords(self.outputs[index])
                        lx1, ly1, lx2, ly2 = self.canvas.coords(line)
                        lx1 = (ox1 + ox2)*0.5
                        ly1 = (oy1 + oy2)*0.5
                        self.canvas.coords(line, lx1, ly1, lx2, ly2)
                    otherIndex += 1

    def draw_input_lines(self):
        index = 0
        for input, dtype, inputName in self.flags['setting']['inputs']:
            if input is not None:
                for block in Block.blocks:
                    otherIndex = 0
                    for output, dtype in block.flags['setting']['outputs']:
                        if output == input:
                            x1, y1, x2, y2 = self.canvas.coords(self.inputs[index])
                            lx2 = (x1+x2)*0.5
                            ly2 = (y1+y2)*0.5
                            x1, y1, x2, y2 = self.canvas.coords(block.outputs[otherIndex])
                            lx1 = (x1+x2)*0.5
                            ly1 = (y1+y2)*0.5
                            line = self.canvas.create_line(lx1, ly1, lx2, ly2, fill='blue')
                            self.inputLines[index] = line
                            block.outputLines[otherIndex].append(line)
                            break
                        otherIndex += 1
            index += 1

    def draw(self):
        self.inputs = []
        self.outputs = []
        self.inputLines = []
        self.outputLines = []
        x, y, w, h, w1, w2 = self.calculate_main_rect()
        self.draw_body(x, y, w, h)
        self.draw_title(x, y, w)
        self.draw_inputs(x, y, w1)
        self.draw_outputs(x, y, w, w1, w2)
        self.draw_input_lines()

    def draw_title(self, x: float, y: float, w: float):
        self.canvas.create_text(x+w*0.5, y-CON_HEIGHT, text=self.flags['setting']['name'], fill='white', font=f'Times {CON_HEIGHT} bold', tags=('block', 'title', self.flags['setting']['name']))

    def draw_body(self, x: float, y: float, w: float, h: float):
        self.canvas.create_rectangle(x, y, x+w, y+h, outline='lightgray', fill='lightgray', tags=('block', 'main', self.flags['setting']['name']))

    def draw_outputs(self, x: float, y: float, w: float, w1: float, w2: float):
        offset = 0
        for output, dtype in self.flags['setting']['outputs']:
            fill = Block.get_dtype_color(dtype)
            self.outputs.append(self.canvas.create_rectangle(x+w+6,y+3+offset,x+w,y+9+offset,outline='white', fill=fill, tags=('block', 'output', self.flags['setting']['name'])))
            self.canvas.create_text(x+w1+w2*0.5, y+6+offset, text=output, fill='darkgreen', tags=('block', 'outtext', self.flags['setting']['name']))
            offset += CON_HEIGHT
            self.outputLines.append([])

    def draw_inputs(self, x: float, y: float, w1: float):
        offset = 0
        for input, dtype, inputName in self.flags['setting']['inputs']:
            fill = Block.get_dtype_color(dtype)
            self.inputs.append(self.canvas.create_rectangle(x-6,y+3+offset,x,y+9+offset,outline='white', fill=fill, tags=('block', 'input', self.flags['setting']['name'])))
            self.canvas.create_text(x+w1*0.5, y+6+offset, text=inputName, fill='black', tags=('block', 'intext', self.flags['setting']['name']))
            offset += CON_HEIGHT
            self.inputLines.append(None)

    @classmethod
    def get_dtype_color(cls, dtype: str) -> str:
        color = None
        if dtype not in cls.dtypes:
            #if new dtype: set random color
            index = randint(0, len(COLORS))
            color = COLORS.pop(index)
            cls.dtypes[dtype] = color
        else:
            #get color associated with dtype
            color = cls.dtypes[dtype]
        return color

    def calculate_main_rect(self):
        #calculate dimensions
        x, y = self.flags['setting']['position']
        w, h = 1, 1
        h += max(len(self.flags['setting']['inputs']), len(self.flags['setting']['outputs']))*CON_HEIGHT
        w2, w1 = 0, 0
        if len(self.flags['setting']['inputs']) > 0:
            w1 = max(len(input[2]) for input in self.flags['setting']['inputs'])*CON_TEXT_WIDTH
        if len(self.flags['setting']['outputs']) > 0:
            w2 = max(len(output[0]) for output in self.flags['setting']['outputs'])*CON_TEXT_WIDTH
        w += w1 + w2
        return x, y, w, h, w1, w2

    def is_owner(self, id: int) -> bool:
        if id in self.canvas.find_withtag(self.flags['setting']['name']):
            return True
        else:
            return False

    def move(self, dx: float, dy: float):
        for id in self.canvas.find_withtag(self.flags['setting']['name']):
            self.canvas.move(id, dx, dy)
        for line in self.inputLines:
            if line is not None:
                x1, y1, x2, y2 = self.canvas.coords(line)
                self.canvas.coords(line, x1, y1, x2+dx, y2+dy)
        for output in self.outputLines:
            for line in output:
                if line is not None:
                    x1, y1, x2, y2 = self.canvas.coords(line)
                    self.canvas.coords(line, x1+dx, y1+dy, x2, y2)
        ids1 = set(self.canvas.find_withtag(self.flags['setting']['name']))
        ids2 = set(self.canvas.find_withtag('main'))
        ids1 &= ids2
        x, y, *_ = self.canvas.coords(ids1.pop())
        self.flags['setting']['position'] = [x, y]

    def on_click(self, event: Event, current: int):
        if current in self.inputs:
            index = self.inputs.index(current)
            self.flags['input'] = [index]
            x1, y1, x2, y2 = self.canvas.coords(current)
            x = (x1+x2)*0.5
            y = (y1+y2)*0.5
            if self.inputLines[index] is None:
                self.inputLines[index] = self.canvas.create_line(x, y, x, y, fill='blue')
                self.flags['input'].append('new')
            else:
                Block.remove_output_line(self.inputLines[index])
                self.flags['input'].append('old')
        else:
            self.flags['grabbed'] = (event.x, event.y)
        self.print_flags()
        return self

    def on_drag(self, event: Event):
        if self.flags['grabbed'] is not None:
            x, y = self.flags['grabbed']
            dx = event.x - x
            dy = event.y - y
            self.flags['grabbed'] = (event.x, event.y)
            self.move(dx, dy)
        elif self.flags['input'] is not None:
            index = self.flags['input'][0]
            line = self.inputLines[index]
            if self.flags['input'][1] == 'new':
                x1, y1, x2, y2 = self.canvas.coords(line)
                self.canvas.coords(line, event.x, event.y, x2, y2)
            elif self.flags['input'][1] == 'old':
                x1, y1, x2, y2 = self.canvas.coords(line)
                self.canvas.coords(line, event.x, event.y, x2, y2)
        elif self.flags['output'] is not None:
            index = self.flags['output'][0]
            line = self.outputLines[index]
            if self.flags['output'][1] == 'new':
                x1, y1, x2, y2 = self.canvas.coords(line)
                self.canvas.coords(line, event.x, event.y, x2, y2)

    def on_release(self, event: Event):
        if self.flags['grabbed'] is not None:
            pass
        elif self.flags['input'] is not None:
            index = self.flags['input'][0]
            line = self.inputLines[index]
            current = self.find_overlapping_mouse(event.x, event.y)
            if len(current) > 0:
                block = None
                for cur in current:
                    for b in self.blocks:
                        if cur in b.outputs and b is not self:
                            block = b
                            current = cur
                            break
                    else:
                        continue
                    break
                if block is not None:
                    otherIndex = block.outputs.index(current)
                    if block.flags['setting']['outputs'][otherIndex][1] == self.flags['setting']['inputs'][index][1]:
                        x1, y1, x2, y2 = self.canvas.coords(current)
                        x = (x1+x2)*0.5
                        y = (y1+y2)*0.5
                        x1, y1, x2, y2 = self.canvas.coords(line)
                        self.canvas.coords(line, x, y, x2, y2)
                        block.outputLines[otherIndex].append(self.inputLines[index])
                        self.flags['setting']['inputs'][index][0] = block.flags['setting']['outputs'][otherIndex][0]
                        if not Block.is_looping(self, index):
                            self.remove_input_line(line, index)
                    else:
                        self.remove_input_line(line, index)
                else:
                    self.remove_input_line(line, index)
            else:
                self.remove_input_line(line, index)
                    
        elif self.flags['output'] is not None:
            pass
        for flag in self.flags:
            if flag not in {'setting'}:
                self.flags[flag] = None

    def remove_input_line(self, line: int, index: int, removeFromSetting=True):
        """Set removeFromSetting to False if you don't want to change setting.
        It will only remove drawing."""
        self.canvas.delete(line)
        self.inputLines[index] = None
        if removeFromSetting:
            self.flags['setting']['inputs'][index][0] = None
        Block.remove_output_line(line)

    def add_input(self, input: list):
        self.flags['setting']['inputs'].append(input)
        self.redraw()

    def add_output(self, output: list):
        self.flags['setting']['outputs'].append(output)
        self.redraw()

    def find_overlapping_mouse(self, x: int, y: int) -> tuple:
        return self.canvas.find_overlapping(x-MOUSE_OFFSET, y-MOUSE_OFFSET, x+MOUSE_OFFSET, y+MOUSE_OFFSET)

    @classmethod
    def remove_output_line(cls, line: int):
        for block in cls.blocks:
            for o, output in enumerate(block.outputLines):
                for l, _line in enumerate(output):
                    if _line == line:
                        block.outputLines[o].pop(l)
    
    @classmethod
    def is_looping(cls, block: object, inputIndex: int) -> bool:
        variables = [block.flags['setting']['inputs'][inputIndex][0]]
        usedInputs = [variables[0]]
        
        while len(variables) > 0:
            for b in cls.blocks:
                for output, dtype in b.flags['setting']['outputs']:
                    if output in variables:
                        variables.pop(variables.index(output))
                        variables.extend([i[0] for i in b.flags['setting']['inputs'] if i[0] is not None])
                        while None in variables: variables.pop(variables.index(None))
                        if all(var not in usedInputs for var in variables):
                            usedInputs.extend([i[0] for i in b.flags['setting']['inputs'] if i[0] is not None])
                            while None in usedInputs: usedInputs.pop(usedInputs.index(None))
                        else: return False
        
        return True
        

class WorkBench(Canvas, Debug):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.flags = {
            'grabbed': None,
        }
        self.pack(fill=BOTH, expand=1)
        self.bind('<ButtonPress-1>', self.on_click)
        self.bind('<B1-Motion>', self.on_drag)
        self.bind('<ButtonRelease-1>', self.on_release)
        self.bind('<ButtonPress-2>', self.add_output_by_name)
        self.blocks = []

    def add_output_by_name(self, name: str, output: list) -> bool:
        block = [b for b in self.blocks if b.flags['setting']['name'] == name]
        if len(block) > 0:
            block = block[0]
            block.add_output(output)
            return True
        else:
            return False

    def add_input_by_name(self, name: str, input: list) -> bool:
        block = [b for b in self.blocks if b.flags['setting']['name'] == name]
        if len(block) > 0:
            block = block[0]
            block.add_input(input)
            return True
        else:
            return False

    def add_block(self, setting: dict):
        duplicate = any(setting['name'] == block.flags['setting']['name'] for block in self.blocks)
        if duplicate:
            raise ValueError(f'Name {setting["name"]} is duplicated.')
        self.blocks.append(Block(self, setting))
        
    def on_click(self, event: Event):
        current = self.find_overlapping(event.x-MOUSE_OFFSET, event.y-MOUSE_OFFSET, event.x+MOUSE_OFFSET, event.y+MOUSE_OFFSET)
        for cur in current:
            if cur in self.find_withtag('block'):
                current = cur
                for block in self.blocks:
                    if block.is_owner(current):
                        self.flags['grabbed'] = block.on_click(event, current)
                        break
                break
        else:
            self.flags['grabbed'] = None

    def on_drag(self, event: Event):
        if self.flags['grabbed'] is not None:
            self.flags['grabbed'].on_drag(event)

    def on_release(self, event: Event):
        if self.flags['grabbed'] is not None:
            self.flags['grabbed'].on_release(event)
            self.flags['grabbed'] = None

class Window(Tk):
    def __init__(self, settings: list, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.canvas = WorkBench(self, bg='black')
        self.canvas.pack(fill=BOTH, expand=1)
        for setting in settings:
            self.canvas.add_block(setting)

if __name__ == "__main__":
    settings = []
    setting = {
        'name': 'in',
        'inputs': [
        ],
        'outputs': [
            ['copy', '3Darray' if randint(0,5)%2 else '2Darray']
        ],
        'position': [50, 50],
    }
    settings.append(setting)
    setting = {
        'name': 'out',
        'inputs': [
            [None, '3Darray' if randint(0,5)%2 else '2Darray', 'input']
        ],
        'outputs': [
        ],
        'position': [50, 50],
    }
    settings.append(setting)
    for key, values in ss.items():
        setting = {
            'name': values[-2],
            'inputs': [
                [values[1], '3Darray' if randint(0,5)%2 else '2Darray', 'input']
            ],
            'outputs': [
                [values[-2], '3Darray' if randint(0,5)%2 else '2Darray']
            ],
            'position': [50, 50],
        }
        settings.append(setting)
    for setting in settings:
        print(setting)
    wnd = Window(settings, )
    wnd.mainloop()