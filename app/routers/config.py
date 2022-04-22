from fastapi import HTTPException,status

COURSE_COLLECTION_NAME = 'course'
CONTENT_COLLECTION_NAME = 'content'
RESOURSE_COLLECTION_NAME = 'resourse'
QUESTION_COLLECTION_NAME = 'question'
FUNCTION_COLLECTION_NAME = 'function'
TESTCASE_COLLECTION_NAME = 'testcase'

CREDENTIALS_EXCEPTION = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )