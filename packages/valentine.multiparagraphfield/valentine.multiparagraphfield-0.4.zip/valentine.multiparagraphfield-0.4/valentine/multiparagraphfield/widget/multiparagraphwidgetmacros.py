from Products.Five import BrowserView

class MacrosView(BrowserView):

    @property
    def macros(self):
        return self.index.macros