import optparse

class Options(optparse.Values):
    def __init__(self, queue=None, window_name='_main'):
        if queue != None: super().__init__({"queue": queue})
        else:             super().__init__()

        self._window_name = window_name

    def progress(self, msg):
        if "queue" in self.__dict__.keys():
            self.queue.put_nowait({"window": self._window_name, "msg": msg})

    def start_doing(self):
        if "queue" in self.__dict__.keys():
            self.queue.put_nowait({"window": self._window_name,
                                   "action": "disable_buttons"})

    def done_doing(self):
        if "queue" in self.__dict__.keys():
            while not self.queue.empty(): self.queue.get_nowait()
            self.queue.put_nowait({"window": self._window_name,
                                   "action": "enable_buttons",
                                   "msg":    "Done"})

    def failed_doing(self, msg, exception=None):
        if "queue" in self.__dict__.keys():
            while not self.queue.empty(): self.queue.get_nowait()
            self.queue.put_nowait({"window":    self._window_name,
                                   "action":    "failure",
                                   "msg":       msg,
                                   "exception": exception})

    def new_pclx_file(self, filename):
        if "queue" in self.__dict__.keys():
            self.queue.put_nowait({"window": self._window_name,
                                   "action": "new_pclx_file",
                                   "filename": filename})
