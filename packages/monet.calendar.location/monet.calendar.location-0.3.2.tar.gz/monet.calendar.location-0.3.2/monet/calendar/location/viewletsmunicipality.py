from monet.calendar.extensions.browser.viewlets import SearchBar
from monet.calendar.location import COMUNI

class SearchBarMunicipality(SearchBar):
    """"""
    
    def getMunicipalityKeysValues(self):
        return COMUNI
    
    def getMunicipalityValue(self,key):
        return COMUNI.getValue(key)
    
    def getDefaultMunicipality(self):
        
        form = self.request.form
        
        if form.has_key('getMunicipality'):
            return form.get('getMunicipality')
        else:
            return '036023'