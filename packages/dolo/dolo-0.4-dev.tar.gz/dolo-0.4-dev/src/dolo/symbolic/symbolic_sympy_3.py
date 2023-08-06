from sympy import Symbol

class TSymbol(Symbol):

    def __init__(self, name, **args):
        print('create something')
        super(TSymbol,self).__init__()
        if 'date' not in args:
            self._assumptions['date'] = 0
        else:
            self._assumptions['date'] = args['date']
        print(self._assumptions)
        return(None)

    def __call__(self, shift):
        current_date = self.assumptions0['date']
        # we forget other assumptions
        v = type(self)
        return v( self.name, date = current_date + shift)

    @property
    def date(self):
        return self.assumptions0['date']

    @property
    def lag(self):
        return self.date

    @property
    def P(self):
        return self(-self.date)


class Variable(TSymbol):
    pass

class Shock(TSymbol):
    pass

class Parameter(Symbol):
    pass