class InvalidToken(Exception):
    def __init__(self,id,detail):
        super().__init__(detail)
        self.id_token = id
        self.detail = detail

class UserNotFound(Exception):
    def __init__(self,user_id,detail):
        self.user_id = user_id
        self.detail = detail

class UnauthorizedOperation(Exception):
    def __init__(self,detail,resource_id):
        super().__init__(detail)
        self.detail = detail
        self.resource_id = resource_id
