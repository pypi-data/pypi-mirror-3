from profile.create.tests import Instrument, Fund, Position, inst_names, \
                                  inst_types, fund_names, inst_ccys,\
                                  fund_ccys, dates, PLEN, populate, zip, test
                                  

class SimpleCreate(test.ProfileTest):
    
    def register(self):
        self.orm.register(Instrument)
        self.orm.register(Fund)
        self.orm.register(Position)
        
    def run(self):
        with Instrument.transaction() as t:
            for name,typ,ccy in zip(inst_names,inst_types,inst_ccys):
                Instrument(name = name, type = typ, ccy = ccy).save(t)
        with Fund.transaction() as t:        
            for name,ccy in zip(fund_names,fund_ccys):
                Fund(name = name, ccy = ccy).save(t)
        instruments = Instrument.objects.all()
        with Position.transaction() as t:
            for f in Fund.objects.all():
                insts = populate('choice',PLEN,choice_from = instruments)
                for dt in dates:
                    for inst in insts:
                        Position(instrument = inst, dt = dt, fund = f).save(t)


