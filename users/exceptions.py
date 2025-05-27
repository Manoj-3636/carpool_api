class InvalidToken(Exception):
    def __init__(self,id,detail):
        super().__init__(detail)
        self.id_token = id
        self.detail = detail

class UserNotFound(Exception):
    def __init__(self,access_token,detail):
        super().__init__(detail)
        self.access_token = access_token