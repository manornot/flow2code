from typing import List
from pydantic import BaseModel, Field


class Block(BaseModel):
    block_id: str = '-1'
    p_code: str = Field(default='', exclude=True)  # Internal storage for `code`, excluded from validation

    # Custom initializer to support passing `code` in the constructor
    def __init__(self, **kwargs):
        code = kwargs.pop('code', '')  # Extract `code` from input arguments
        super().__init__(**kwargs)  # Initialize other fields with Pydantic's logic
        self.p_code = code  # Manually assign `_code`
    
    @property
    def code(self):
        return [self.p_code]


class Input(Block):
    @property
    def code(self):
        var_name, var_type = self.p_code.split(':')
        num_types = ['int', 'integer', 'number', 'float']
        str_types = ['string', 'text', 'str', 'words', 'word', 'name']
        arr_types = ['array[int]', 'array[float]', 'array[numbers]', 'array[digits]',
                     'list[int]', 'list[float]', 'list[numbers]', 'list[digits]']

        if var_type in num_types:
            var_type = 'float' if var_type not in ['int', 'integer'] else 'int'
            return [f'{var_name} = {var_type}(input())']
        elif var_type in str_types:
            return [f'{var_name} = input()']
        elif var_type in arr_types:
            element_type = 'float' if 'float' in var_type else 'int'
            return [
                f'data = [{element_type}(i) for i in input(f"Enter values of type {element_type} separated by \',\'").split(\',\')]']
        else:
            return [self.p_code]

class Output(Block):
    @property
    def code(self):
        return [f'print({self.p_code})']

class IfStatement(Block):
    condition: str = ''
    true_branch_body: List[List[Block]] = Field(default_factory=list)
    false_branch_body: List[List[Block]] = Field(default_factory=list)
    
    @property
    def code(self):
        # Only return the condition and structure
        return [f'if {self.condition}:']


class Loop(Block):
    body: List[List[Block]] = Field(default_factory=list)
    
    def add_block_to_body(self, block):
        self.body.append(block)

class WhileLoop(Loop):
    condition: str = ''


class RepeatLoop(Loop):
    counter: str = ''

    @property
    def code(self) -> list:
        return [
            [f'for _cntr_ in range({self.counter}):'], #repeat {self.counter} times
            [block.code for block in self.body]
            ]

class ForEachLoop(Loop):
    iterator_var: str = ''





    
    