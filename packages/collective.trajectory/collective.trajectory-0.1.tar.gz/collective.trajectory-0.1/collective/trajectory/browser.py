from Products.Five import BrowserView

class DefaultIndex(BrowserView):
    def repr(self):
        return str(self.context)
