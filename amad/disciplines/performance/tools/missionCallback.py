def empty_callback(*kwargs):
    pass


class MissionCallback:
    def __init__(self):
        self.callback_method = empty_callback

    def callback(self, callback_data):
        self.callback_method(callback_data)


if __name__ == "__main__":

    def print_callback(callback_data):
        print(callback_data)

    mc = MissionCallback()
    mc.callback(callback_data="hello world")

    mc.callback_method = print_callback
    mc.callback(callback_data="hello world")
