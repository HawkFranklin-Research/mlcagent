from textual.widgets import RichLog


class LogStream(RichLog):
    def __init__(self,**kwargs):
        super().__init__(markup=False,highlight=False,wrap=True,**kwargs)
