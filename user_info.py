class UserInfo:

    def __init__(self, name, address, sock=None):
        self.name = name
        self.address = address
        self.sock = sock

    def __eq__(self, obj):
        return isinstance(obj, UserInfo) and obj.address == self.address

    def __str__(self):
        return f"User with name: {self.name} and address: {self.address}"