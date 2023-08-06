class StoreScrapError(Exception):
    def __init__(self, message):
        super(StoreScrapError, self).__init__(message)
