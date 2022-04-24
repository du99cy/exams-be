from ...function.model import Function
from typing import List
from ...testcase.model import Testcase


class Language:

    def __init__(self, func: Function, function_scripts: str, testcase_list: List[Testcase]) -> None:
        self.func = func

        self.function_scripts = function_scripts
        self.testcase_list = testcase_list
    # return file name

    async def generate_build_file(self) -> str:
        pass

    async def run_testcase(self):
        pass
