from ..coding_config import LANGUAGE_SYNTAX_DATA
from ...function.model import Function
from ...testcase.model import OutputTestCase


class CodeTemplate:

    def __init__(self, language_pro_name: str, func: Function) -> None:
        self.language_pro_name = language_pro_name.strip().lower()
        self.func = func

    def __str__(self) -> str:
        params_string = ','.join((f'{LANGUAGE_SYNTAX_DATA[self.language_pro_name]["data_type"][param.datatype.strip().lower()]} {param.name}'
                                  for param in self.func.inputs)) if self.language_pro_name in {'cpp', 'java'} else ','.join((f'{param.name}:{LANGUAGE_SYNTAX_DATA[self.language_pro_name]["data_type"][param.datatype.strip().lower()]}'
                                                                                                                              for param in self.func.inputs))

        data_format = {'output_type': LANGUAGE_SYNTAX_DATA[self.language_pro_name]['data_type']
                       [self.func.output_data_type], 'func_name': self.func.name, 'params': params_string}

        template = LANGUAGE_SYNTAX_DATA[self.language_pro_name]['format'].format(
            **data_format)

        if ('string' in (ip.datatype for ip in self.func.inputs) or self.func.output_data_type == 'string') and self.language_pro_name == 'cpp':
            template = '#include <string>\n\n'+template

        return template
