class InvalidToken(Exception):
    def __init__(self,id,detail):
        super().__init__(detail)
        self.id_token = id
        self.detail = detail