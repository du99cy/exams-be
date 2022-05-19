from unittest import TestCase
from routers.function.model import Function
from .language_interface import Language
from ..coding_config import LANGUAGE_SYNTAX_DATA, SOURCE_CODE_FILE
from bson.objectid import ObjectId
import aiofiles
import asyncio,shlex,ast
import os,re,subprocess
from typing import List
class Cpp(Language):

    def __init__(self, func: Function, function_scripts: str, testcase_list: List[TestCase]) -> None:
        super().__init__(func, function_scripts, testcase_list)
    # return file name

    async def generate_build_file(self) -> str:
        header = "#include <iostream>\n#include <string>\n#include <thread>\n#include <assert.h>"

        options = [
            "cxxopts::Options options(\"AIV\", \"Kiem tra danh gia\");\n\toptions.add_options()"]

        declarations = []
        # for caller function
        params_str = []
        for param in self.func.inputs:
            ten_dau_vao = param.name
            kieu_du_lieu_generic = param.datatype.strip().lower()
            cpp_data_type = LANGUAGE_SYNTAX_DATA['cpp']['data_type'][kieu_du_lieu_generic]

            if ten_dau_vao != 'output':
                params_str.append(ten_dau_vao)

            options.append('\t("{}", "", cxxopts::value<{}>())'.format(
                ten_dau_vao, cpp_data_type))
            declarations.append('{data_type} {param_name} = result["{param_name}"].as<{data_type}>();\n'.format(
                **{'data_type': cpp_data_type, 'param_name': ten_dau_vao}))

        caller = '{0}({1})'.format(self.func.name, ", ".join(params_str))

        main = '''
        int main (int argc, char *argv[]) {{ 
        \n    {}\t;
        \n    auto result = options.parse(argc, argv); 
        \n    {}  
        \n    auto r = {}; 
        \n    std::cout <<r;
        \n    return 0;      
        \n}}'''.format('\n\t'.join(options), '\n\t'.join(declarations), caller)

        file_content = f'{header}\n{self.function_scripts}\n{main}'
        
        #make unique file name
        file_name = str(ObjectId())
        #file to write code to build
        file_path = f'{SOURCE_CODE_FILE}/cpp/{file_name}.cc'

        async with aiofiles.open(file_path,mode='w') as f:
                await f.write(file_content)

        return file_name

    async def run_testcase(self):
        output_result = []
        
        file_name = await self.generate_build_file()
        
        #Build C++ file of user
        #build_file_cpp_cmd = "g++ {1}/cpp/{0}.cc -Wall -fconcepts -o {1}/cpp/{0}".format(file_name,SOURCE_CODE_FILE)
        build_file_cpp_cmd = 'g++ -O -Wall {file_name}.C -o executable'
        
        build_proc = await asyncio.create_subprocess_exec(*shlex.split(build_file_cpp_cmd), stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        _, compile_error = await build_proc.communicate()
        
        if compile_error.decode() != '':
            return {'is_compile_error':True,'detail': compile_error.decode()}
        #return a string like --param1 or -p
        gen_argument_valid = lambda ten_dau_vao:f'--{ten_dau_vao}' if (len(ten_dau_vao) > 1) else f'-{ten_dau_vao}'

        # Run with testcase
        process_list = {}
        for testcase in self.testcase_list:
            #format like --param1 12 --param2 23
            #or -a 1 -b 2
            #or --param1 1 -b 3
            params_string = ' '.join(('{var_name} {value}'.format(**{
                'var_name':gen_argument_valid(param.name),
                'value':re.sub(r'\[|\]|\s','',param.value)
                }
            ) 
            for param in testcase.inputs))       
            cmd_run_testcase = '{SOURCE_CODE_FILE}/cpp/{}  {}'.format(file_name, params_string)

            proc = subprocess.Popen([cmd_run_testcase],stdout = subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
        
            process_list.update({proc:testcase})

        is_all_process_finished = lambda : all([proc.poll() != None for proc in process_list])

        while True:
            if is_all_process_finished:
                for proc in process_list:
                    testcase = process_list[proc]
                    outs,errs = proc.communicate()
                    
                    errs = errs.decode()
                    outs = ast.literal_eval(outs.decode()) if errs=='' else None 

                    passed = outs == ast.literal_eval(testcase.output.value)
                    score = 1 if passed else 0
                    

                    data_returned = {"id": testcase["id"],
                                    "expected_output":testcase.output.value,
                                    "user_output": outs,
                                    "score": score,
                                    "expected_output":errs,
                                    "locked": testcase.lock,
                                    "passed": passed}
                    output_result.append(data_returned)
                break

        #remove file from src/cpp and bin/cpp
        subprocess.Popen([f'rm {SOURCE_CODE_FILE}/cpp/{file_name}.cc'],shell=True)
        subprocess.Popen([f'rm {SOURCE_CODE_FILE}/cpp/{file_name}'],shell = True)
        
        return output_result