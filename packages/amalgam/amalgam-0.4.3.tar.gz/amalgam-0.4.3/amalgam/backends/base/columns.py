class BaseColumns(object):
    @staticmethod
    def String(**kwargs):
        raise NotImplementedError()

    @staticmethod
    def Text(**kwargs):
        raise NotImplementedError()

    @staticmethod
    def Boolean(**kwargs):
        raise NotImplementedError()

    @staticmethod
    def Integer(**kwargs):
        raise NotImplementedError()

    @staticmethod
    def Float(**kwargs):
        raise NotImplementedError()

    @staticmethod
    def Decimal(**kwargs):
        raise NotImplementedError()

    @staticmethod
    def DateTime(**kwargs):
        raise NotImplementedError()

    @staticmethod
    def Date(**kwargs):
        raise NotImplementedError()

    @staticmethod
    def Time(**kwargs):
        raise NotImplementedError()
