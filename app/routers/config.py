from fastapi import HTTPException,status

USER_COLLECTION = 'user'
COURSE_COLLECTION_NAME = 'course'
CONTENT_COLLECTION_NAME = 'content'
RESOURSE_COLLECTION_NAME = 'resourse'
QUESTION_COLLECTION_NAME = 'question'
FUNCTION_COLLECTION_NAME = 'function'
TESTCASE_COLLECTION_NAME = 'testcase'
TRANSACTION_COLLECTION_NAME = 'transaction'


CREDENTIALS_EXCEPTION = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

RESOURSE_FILE_NAME = 'resourse-files'
STATIC_FILE = 'static-files'