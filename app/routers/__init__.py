from .test import api_router as TestRouter
from .course import course_router
from .content import apiRouter as ContentRouter
from .resourse import api_router as ResourseRouter
api_router_list = [
    {"name":TestRouter},
    {"name":course_router},
    {"name":ContentRouter},
    {"name":ResourseRouter},
]