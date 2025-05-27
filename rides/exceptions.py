class RideNotFound(Exception):
    def __init__(self,detail,_id):
        super().__init__(detail)
        self.id = _id
        self.detail = detail
