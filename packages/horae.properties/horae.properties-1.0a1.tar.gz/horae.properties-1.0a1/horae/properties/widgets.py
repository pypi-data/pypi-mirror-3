from zope.formlib.itemswidgets import ItemDisplayWidget as BaseItemDisplayWidget

from horae.properties import _


class ItemDisplayWidget(BaseItemDisplayWidget):

    def __call__(self):
        """See IBrowserWidget."""
        value = self._getFormValue()
        if value is None or value == u'':
            return self.translate(self._messageNoValue)
        else:
            if not value in self.vocabulary:
                return self.translate(_(u'${value} (value no longer in vocabulary)', mapping=dict(value=value)))
            term = self.vocabulary.getTerm(value)
            return self.textForValue(term)
