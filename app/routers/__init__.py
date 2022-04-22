from .test import api_router as TestRouter
from .course import course_router
from .content import apiRouter as ContentRouter
from .resourse import api_router as ResourseRouter
from .question import QuestionRouter
from .function import FunctionRouter
from .testcase import TestcaseRouter
api_router_list = [
    {"name":TestRouter},
    {"name":course_router},
    {"name":ContentRouter},
    {"name":ResourseRouter},
    {"name":QuestionRouter},
    {"name":FunctionRouter},
    {"name":TestcaseRouter}
]