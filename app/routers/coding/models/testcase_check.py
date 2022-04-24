from unittest.mock import Base
from pydantic import BaseModel
from ...function.model import Parameter
from ...testcase.model import OutputTestCase
from typing import List

class Testcase_Check(BaseModel):
    id:str | None = None
    inputs:List[Parameter] | None = []
    user_output:str | None = None
    expected_output:str | None = None
    score:int | None = None
    exception:str | None = None
    passed:bool | None = False
    locked:bool | None = False