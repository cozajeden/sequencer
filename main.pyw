from tkinter import *
from settings import settings as ss
from random import randint

MOUSE_OFFSET = 2

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
        self.setting = setting
        self.canvas = canvas
        self.inputs = []
        self.inputLines = []
        self.outputs = []
        self.outputLines = []
        self.texts = []
        #calculate dimensions
        x, y = setting['position']
        w, h = 1, 1
        h += max(len(setting['inputs']), len(setting['outputs']))*12
        w2, w1 = 0, 0
        if len(setting['inputs']) > 0:
            w1 = max(len(input[2]) for input in setting['inputs'])*7
        if len(setting['outputs']) > 0:
            w2 = max(len(output[0]) for output in setting['outputs'])*7
        w += w1 + w2
        #create body
        self.id = canvas.create_rectangle(x, y, x+w, y+h, outline='lightgray', fill='lightgray', tags=('block', setting['name']))
        #draw title
        self.name = canvas.create_text(x+w*0.5, y-12, text=setting['name'], fill='white', font='Times 12 bold', tags=('block', setting['name']))
        offset = 0
        #draw inputs
        for input, dtype, inputName in setting['inputs']:
            #if new dtype: set random color
            if dtype not in Block.dtypes:
                Block.dtypes[dtype] = f'#{randint(0, 255):02x}{randint(0, 255):02x}{randint(0, 255):02x}'
            #get color associated with dtype
            fill = Block.dtypes[dtype]
            self.inputs.append(canvas.create_rectangle(x-6,y+3+offset,x,y+9+offset,outline=fill, fill=fill, tags=('block', 'input', setting['name'])))
            canvas.create_text(x+w1*0.5, y+6+offset, text=inputName, fill='black', tags=('block', setting['name']))
            offset += 12
            self.inputLines.append(None)
        offset = 0
        #draw outputs
        for output, dtype in setting['outputs']:
            if dtype not in Block.dtypes:
                Block.dtypes[dtype] = f'#{randint(0, 255):02x}{randint(0, 255):02x}{randint(0, 255):02x}'
            fill = Block.dtypes[dtype]
            self.outputs.append(canvas.create_rectangle(x+w+6,y+3+offset,x+w,y+9+offset,outline=fill, fill=fill, tags=('block', 'output', setting['name'])))
            canvas.create_text(x+w1+w2*0.5, y+6+offset, text=output, fill='darkgreen', tags=('block', setting['name']))
            offset += 12
            self.outputLines.append([])
        self.flags = {
            'grabbed': None,
            'output': None,
            'input': None,
            'templine': None,
        }
        Block.blocks.append(self)

    def is_owner(self, id):
        if id in self.canvas.find_withtag(self.setting['name']):
            return True
        else:
            return False

    def move(self, dx, dy):
        for id in self.canvas.find_withtag(self.setting['name']):
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

    def on_click(self, event, current):
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

    def on_drag(self, event):
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

    def on_release(self, event):
        if self.flags['grabbed'] is not None:
            pass
        elif self.flags['input'] is not None:
            index = self.flags['input'][0]
            line = self.inputLines[index]
            current = self.canvas.find_overlapping(event.x-MOUSE_OFFSET, event.y-MOUSE_OFFSET, event.x+MOUSE_OFFSET, event.y+MOUSE_OFFSET)
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
                    if block.setting['outputs'][otherIndex][1] == self.setting['inputs'][index][1]:
                        x1, y1, x2, y2 = self.canvas.coords(current)
                        x = (x1+x2)*0.5
                        y = (y1+y2)*0.5
                        x1, y1, x2, y2 = self.canvas.coords(line)
                        self.canvas.coords(line, x, y, x2, y2)
                        block.outputLines[otherIndex].append(self.inputLines[index])
                        self.setting['inputs'][index][0] = block.setting['outputs'][otherIndex][0]
                        Block.check_for_loops(self, index)
                    else:
                        self.remove_input_line(line, index)
                else:
                    self.remove_input_line(line, index)
            else:
                self.remove_input_line(line, index)
                    
        elif self.flags['output'] is not None:
            pass
        for flag in self.flags:
            self.flags[flag] = None

    def remove_input_line(self, line, index):
        self.canvas.delete(line)
        self.inputLines[index] = None
        self.setting['inputs'][index][0] = None
        Block.remove_output_line(line)

    @classmethod
    def remove_output_line(cls, line):
        for block in cls.blocks:
            for o, output in enumerate(block.outputLines):
                for l, _line in enumerate(output):
                    if _line == line:
                        block.outputLines[o].pop(l)
    
    @classmethod
    def check_for_loops(cls, block, inputIndex) -> bool:
        variables = [block.setting['inputs'][inputIndex][0]]
        usedInputs = [variables[0]]
        
        while len(variables) > 0:
            for b in cls.blocks:
                for output, dtype in b.setting['outputs']:
                    if output in variables:
                        variables.pop(variables.index(output))
                        variables.extend([i[0] for i in b.setting['inputs'] if i[0] is not None])
                        while None in variables: variables.pop(variables.index(None))
                        if all(var not in usedInputs for var in variables):
                            usedInputs.extend([i[0] for i in b.setting['inputs'] if i[0] is not None])
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
        self.blocks = []

    def add_block(self, setting):
        duplicate = any(setting['name'] == block.setting['name'] for block in self.blocks)
        if duplicate:
            raise ValueError(f'Name {setting["name"]} is duplicated.')
        self.blocks.append(Block(self, setting))
        
    def on_click(self, event):
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

    def on_drag(self, event):
        if self.flags['grabbed'] is not None:
            self.flags['grabbed'].on_drag(event)

    def on_release(self, event):
        if self.flags['grabbed'] is not None:
            self.flags['grabbed'].on_release(event)
            self.flags['grabbed'] = None

class Window(Tk):
    def __init__(self, settings, *args, **kwargs):
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
                [None, '3Darray' if randint(0,5)%2 else '2Darray', 'input']
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