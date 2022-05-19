import ast
import traceback
from .language_interface import Language
from bson.objectid import ObjectId
import aiofiles
from ..coding_config import SOURCE_CODE_FILE
from ...function.model import Function
from ...testcase.model import Testcase
from typing import List
import concurrent.futures
from .testcase_check import Testcase_Check


class Python(Language):

    def __init__(self, func: Function, function_scripts: str, testcase_list: List[Testcase]) -> None:
        super().__init__(func, function_scripts, testcase_list)

    # for python do not need to gen build file just write file to folder source-code-files
    async def generate_build_file(self) -> str:
        file_name = str(ObjectId())
        async with aiofiles.open(f'{SOURCE_CODE_FILE}/python/{file_name}.py', mode='w') as f:
            await f.write(self.function_scripts)
        return file_name

    async def get_result(self):
        new_testcase_list = []
        # get file name of source code of user
        sourcecode_file_name = await self.generate_build_file()
        # import from module sourcecode_file_name
        module = __import__(
            f'{SOURCE_CODE_FILE}.python.{sourcecode_file_name}', fromlist=[None])
        # get function from that module
        func_name = getattr(module, self.func.name)
        # run testcase list
        for testcase in self.testcase_list:
            # format of testcase in DB in file language_generic.py
            testcase_id = {'id': testcase.id}
            testcase_input = {'inputs': {ip.name: ast.literal_eval(
                ip.value) for ip in testcase.inputs}}
            testcase_output = {
                'output': ast.literal_eval(testcase.output.value)}
            testcase_initial_inputs = {"testcase_initial_inputs":testcase.inputs}
            new_testcase_list.append(
                {**testcase_id, **testcase_input, **testcase_output,**testcase_initial_inputs, 'hidden': testcase.lock})

        data_returned = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:

            future_to_url = {executor.submit(
                func_name, **testcase['inputs']): testcase for testcase in new_testcase_list}

            for future in concurrent.futures.as_completed(future_to_url):

                testcase = future_to_url[future]

                exp = future.exception()

                r = future.result() if exp == None else None

                score = 1 if r == testcase['output'] else 0

                passed = True if score == 1 else False

                testcase_check = Testcase_Check(
                    id=testcase['id'], expected_output=testcase['output'], inputs=testcase["testcase_initial_inputs"], user_output=str(r), score=score, exception=str(exp), passed=passed)
                # data_returned.append({'id': testcase['id'],
                #                       "expected_ouput": testcase["output"],
                #                       "output": r,
                #                       "score": score,
                #                       "exception": str(exp),
                #                       "hidden": testcase["hidden"]})
        # when finished program then remove that file
        # remove_source_code_cmd = f'rm src/python/{sourcecode_file_name}.py'
        # subprocess.Popen([remove_source_code_cmd],shell = True)

                data_returned.append(testcase_check)

        return data_returned

    async def run_testcase(self):
        try:
            result = await self.get_result()
            return result

        except Exception as exp:
            exp_detail = traceback.format_exc()
            
            return {'is_compile_error': True, 'detail': exp_detail}

        finally:
            pass
