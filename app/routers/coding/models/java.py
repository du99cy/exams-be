from pathlib import Path
from shlex import shlex
from sys import stderr, stdout
from routers.coding.models.testcase_check import Testcase_Check
from routers.testcase.model import Testcase

from routers.function.model import Function
from .language_interface import Language
from bson.objectid import ObjectId
import os
import aiofiles
import subprocess
from typing import List

import re,ast
from ..coding_config import LANGUAGE_SYNTAX_DATA, SOURCE_CODE_FILE

class Java(Language):
    OUTPUT_FILE_NAME = 'MainClass.java'

    def __init__(self, func: Function, function_scripts: str, testcase_list: List[Testcase]) -> None:
        super().__init__(func, function_scripts, testcase_list)

    async def generate_build_file(self) -> str:

        # fill code into MainClass.java
        folder_name = str(ObjectId())
        
        folder_path = f'{SOURCE_CODE_FILE}/java/{folder_name}'
        cmd = f'mkdir {folder_path}'
        # create folder on user own
        s = subprocess.Popen([cmd], stderr=subprocess.PIPE,
                             stdout=subprocess.PIPE, shell=True)

        #wait for finishes the process
        s.wait()


        import shutil
        # copy commons-cli-1.4.jar to the folder that have been created
        lib_file_path = os.path.join(os.path.dirname(
            __file__), 'java_lib', 'commons-cli-1.4.jar')

        shutil.copy2(lib_file_path, folder_path)
        #read from skeleton of a java program 
        txt = Path(os.path.join(os.path.dirname(__file__),
                   'java_lib', 'template.java')).read_text()

        txt = txt.replace('//injection code', self.function_scripts)

        option_params = '\n\t'.join([f"options.addOption(\"{param.name}\", true, \"Enter this required argument\");" for param in self.func.inputs])
        
        txt = txt.replace('//option params', option_params)

        getOptionValues = '\n\t'.join(["String arg_{0} = cmd.getOptionValue(\"{0}\");".format(param.name) for param in self.func.inputs])
            
        txt = txt.replace('// getOptionValues', getOptionValues)
        #make regex
        
        #convert data type 
        convertParamType = '\n\t'.join(["{data_type_java} input_{variable_name} = {convert_function_name}(arg_{variable_name});".format(**{
            'data_type_java':LANGUAGE_SYNTAX_DATA['java']['data_type'][param.datatype.strip().lower()],
            'convert_function_name':"parse_" + re.sub(r'\[|\]','_',param.datatype.strip().lower()),
            'variable_name':param.name
        }) for param in self.func.inputs ])
        
        txt = txt.replace('// convertParamType', convertParamType)

        #call function_user to main func 
        callMainFuntion_params = (',').join(
            ['input_' + param.name for param in self.func.inputs])
        callMainFunction = "result = {}({});\n \t".format(
            self.func.name, callMainFuntion_params)
        txt = txt.replace('// callMainFunction', callMainFunction)

        #write to MainClass.java file 

        async with aiofiles.open(os.path.join(folder_path,self.OUTPUT_FILE_NAME), mode="w") as f:
            await f.write(txt)
        
        # compile java
        print(self.OUTPUT_FILE_NAME)
        compile_java_cmd = f'cd {folder_path} && javac -cp commons-cli-1.4.jar {self.OUTPUT_FILE_NAME}'

        #execute cmd to compile java program

        result = subprocess.Popen([compile_java_cmd],stderr=subprocess.PIPE,stdout=subprocess.PIPE,shell = True)
        
        _, compile_err = result.communicate()

        compile_err = compile_err.decode()
        

        return {'folder_name':folder_name} if compile_err == '' else {'is_compile_error':True,'detail':compile_err}

    async def run_testcase(self):
        result = await self.generate_build_file()
        
        if result.get('is_compile_error'):
            return result
        #else
        folder_name = result['folder_name']
        output_result = []
        #list of subprocess
        process_list = {}
        for unit_test in self.testcase_list:
            print("unit_test",unit_test)
            param_str = ' '.join(['-{0} {1}'.format(
                param.name,
                re.sub(r'\[|\]','',param.value).replace(" ","")
            ) 
            for param in unit_test.inputs])
            
            java_program_run_cmd = f'cd {SOURCE_CODE_FILE}/java/{folder_name} && java -cp commons-cli-1.4.jar: MainClass {param_str}'

            proc = subprocess.Popen([java_program_run_cmd],stderr = subprocess.PIPE,stdout=subprocess.PIPE,shell=True)
            
            process_list.update({proc:unit_test})
        
        is_all_process_finished  = lambda : all([proc.poll() != None for proc in process_list])

        while True:
            if is_all_process_finished:
                for proc in process_list:

                    unit_test = process_list[proc]

                    outs,errs = proc.communicate()
                    
                    errs = errs.decode()
                    outs = ast.literal_eval(outs.decode()) if errs == '' else None
                    score =1 if outs == ast.literal_eval(unit_test.output.value) else 0
                    passed = True if outs == ast.literal_eval(unit_test.output.value) else False
                    data_returned = {"id": unit_test.id,
                                    "expected_output":unit_test.output.value,
                                    "user_output": outs,
                                    "score": score,
                                    "passed":passed,
                                    "exception":errs,
                                    "locked": unit_test.lock,
                                    'inputs':unit_test.inputs,
                                    }
                    testcase_check = Testcase_Check(**data_returned)
                    output_result.append(testcase_check)
                break
        
        #release folder/remove folder
        remove_folder_cmd = f'rm -rf {SOURCE_CODE_FILE}/java/{folder_name}'
        #execute
        execute_remove_folder_cmd = subprocess.Popen([remove_folder_cmd],shell=True)
        execute_remove_folder_cmd.wait()
        #last, return output
        return output_result 
