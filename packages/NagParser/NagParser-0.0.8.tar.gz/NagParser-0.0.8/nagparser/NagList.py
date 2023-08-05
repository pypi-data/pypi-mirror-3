class NagList(list):
    def __getattr__(self, name):
        _name = str(name).replace('_', '-')
        obj = filter(lambda x: x.name == _name, self)
        
        if obj:
            if len(obj) == 1:
                return obj[0]
            else:
                raise AttributeError('Multiple instances found')
            
        elif name == 'names':
            results = []
            for obj in self:
                results.append(obj.name)
                
            return results
        elif name == 'first':
            if self:
                return self[0]
            else:
                return None
        else:
            raise AttributeError