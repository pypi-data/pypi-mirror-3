from plone.indexer.decorator import indexer
from monet.calendar.event.interfaces import IMonetEvent

@indexer(IMonetEvent)
def comune_title(object, **kw):
    try:
        cod_com = object.getMunicipality()
        if not cod_com:
            return ''
        vocab = object.restrictedTraverse('vocabolari')
        com_voc = vocab.getVoc('COMUNI')
        tit = com_voc.items()[com_voc.keys().index(cod_com)][1]
        return tit
    except:
        return ''