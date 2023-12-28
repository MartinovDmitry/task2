from fastapi import HTTPException, status


class MyException(HTTPException):
    status_code = 500
    detail = ''

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)


class NotFoundError(MyException):
    status_code = status.HTTP_204_NO_CONTENT
    detail = 'No content'


class IncorrectContentTypeError(MyException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = 'Content type of file has to be CSV'
