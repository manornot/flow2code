import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.generator.blockModel import Block, IfStatement, Loop, WhileLoop, RepeatLoop, ForEachLoop, Input, Output
from typing import List

class CodeGenerationManager:
    def __init__(self, indent_size=4):
        self._code_blocks: List[Block] = []
        self._indent_size = indent_size

    def add_block(self, line):
        self._code_blocks.append(line)

    def process_blocks(self) -> List[List]:
        """
        Process the blocks and return a 2-by-n list containing:
        - The indentation level (integer).
        - The code block (string or list of strings).
        """
        processed = []
        for block in self._code_blocks:
            processed.extend(self.process_block(block))
        return processed

    def process_block(self, block, current_indent=0) -> List[List]:
        """
        Recursively process blocks and return a 2-by-n list containing:
        - The indentation level (integer).
        - The code block (string or list of strings).
        """
        processed = []

        # Base case: If the block is a simple Block, return its code

        # Handle IfStatement
        if isinstance(block, IfStatement):
            # Add the condition block
            processed.append([block.block_id, current_indent, block.code])

            # Process true_branch_body
            for true_block in block.true_branch_body:
                processed.extend(self.process_block(true_block, current_indent + 1))

            # Add the else branch if it exists
            if block.false_branch_body:
                processed.append([block.block_id, current_indent, ['else:']])
                for false_block in block.false_branch_body:
                    processed.extend(self.process_block(false_block, current_indent + 1))

        # Handle Loop and its derivatives
        elif isinstance(block, Loop):
            if isinstance(block, WhileLoop):
                processed.append([block.block_id, current_indent, [f'while {block.condition}:']])
            elif isinstance(block, RepeatLoop):
                processed.append([block.block_id, current_indent, [f'for _cntr_ in range({block.counter}):']])
            elif isinstance(block, ForEachLoop):
                processed.append([block.block_id, current_indent, [f'for {block.iterator_var} in collection:']])

            # Process the body of the loop
            for body_block in block.body:
                processed.extend(self.process_block(body_block, current_indent + 1))
        elif block.__class__ in (Block, Input, Output) and not hasattr(block, 'true_branch_body'):
            processed.append([block.block_id, current_indent, block.code])
            return processed



        return processed


if __name__ == "__main__":
    # Example usage

    blk = Block(code='print("Hello, World!")\nprint("This is a block")\nprint("This is another block")')

    if_stmt = IfStatement(condition='x > 10', true_branch_body=[[blk], [blk], [blk]],
                          false_branch_body=[[Block(code='print("x is not greater than 10")')]])

    blk_counter_log = Block(code=f'print("Iteration", {{i}})')
    repeat_loop = RepeatLoop(counter='i', body=[[blk_counter_log], [if_stmt]])

    forEach_loop = ForEachLoop(iterator_var='item', body=[[Block(code=f'print("Item:", {{item}})')]])

    cgm = CodeGenerationManager()

    cgm.add_block(blk)
    cgm.add_block(if_stmt)
    cgm.add_block(repeat_loop)
    cgm.add_block(blk)
    code_prep = cgm.process_blocks()
    print(code_prep)