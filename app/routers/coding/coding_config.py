LANGUAGE_SYNTAX_DATA = {'cpp': {'data_type': {'integer': 'int', 'character': 'char', 'string': 'string', 'boolean': 'bool',
                                      'float': 'float', 'double': 'double', 'void': 'void',
                                      'array[integer]': 'std::vector<int>', 'array[char]': 'std::vector<char>', 'array[boolean]': 'std::vector<bool>',
                                      'array[float]': 'std::vector<float>', 'array[double]': 'std::vector<double>'},
                        'format': '{output_type} {func_name}({params}){{\n\treturn ;\n}}'},
                'java': {'data_type': {'integer': 'int', 'character': 'char', 'string': 'String', 'boolean': 'boolean',
                                       'float': 'float', 'double': 'double', 'void': 'void',
                                       'array[integer]': 'int[]', 'array[char]': 'char[]', 'array[boolean]': 'boolean[]',
                                       'array[float]': 'float[]', 'array[double]': 'double[]','array[string]': 'String[]'},
                         'format': '{output_type} {func_name}({params}){{\n\treturn ;\n}}'},
                'python': {'data_type': {'integer': 'int', 'string': 'str', 'float': 'float', 'void': 'None', 'boolean': 'bool',
                                         'array[integer]': 'list', 'array[char]': 'list', 'array[boolean]': 'list',
                                         'array[float]': 'list', 'array[double]': 'list'},
                           'format': 'def {func_name}({params}) -> {output_type}:\n    return'}
                }

SOURCE_CODE_FILE = 'source-code-files'