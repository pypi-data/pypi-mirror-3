
from twisted.trial import unittest
from zope.interface import implements

from txtorcon import Circuit, Stream
from txtorcon.interface import IRouterContainer, ICircuitListener, ICircuitContainer

class FakeTorController(object):
    implements(IRouterContainer, ICircuitListener, ICircuitContainer)
    
    def __init__(self):
        self.routers = {}
        self.circuits = {}
        self.extend = []
        self.failed = []
    def router_from_id(self, i):
        return self.routers[i]
    def circuit_new(self, circuit):
        self.circuits[circuit.id] = circuit
    def circuit_extend(self, circuit, router):
        self.extend.append((circuit, router))
    def circuit_launched(self, circuit):
        pass
    def circuit_built(self, circuit):
        pass
    def circuit_closed(self, circuit):
        if self.circuits.has_key(circuit.id):
            del self.circuits[circuit.id]
    def circuit_failed(self, circuit, reason):
        self.failed.append((circuit,reason))
        if self.circuits.has_key(circuit.id):
            del self.circuits[circuit.id]
    def find_circuit(self, circid):
        return self.circuits[circid]
        
class FakeLocation:
    def __init__(self):
        self.countrycode = 'NA'
class FakeRouter:
    def __init__(self, hsh, nm):
        self.name = nm
        self.hash = hsh
        self.location = FakeLocation()

examples = [
    'CIRC 365 LAUNCHED PURPOSE=GENERAL',
    'CIRC 365 EXTENDED $E11D2B2269CC25E67CA6C9FB5843497539A74FD0=eris PURPOSE=GENERAL',
    'CIRC 365 EXTENDED $E11D2B2269CC25E67CA6C9FB5843497539A74FD0=eris,$50DD343021E509EB3A5A7FD0D8A4F8364AFBDCB5=venus PURPOSE=GENERAL',
    'CIRC 365 EXTENDED $E11D2B2269CC25E67CA6C9FB5843497539A74FD0=eris,$50DD343021E509EB3A5A7FD0D8A4F8364AFBDCB5=venus,$253DFF1838A2B7782BE7735F74E50090D46CA1BC=chomsky PURPOSE=GENERAL',
    'CIRC 365 BUILT $E11D2B2269CC25E67CA6C9FB5843497539A74FD0=eris,$50DD343021E509EB3A5A7FD0D8A4F8364AFBDCB5=venus,$253DFF1838A2B7782BE7735F74E50090D46CA1BC=chomsky PURPOSE=GENERAL',
    'CIRC 365 CLOSED $E11D2B2269CC25E67CA6C9FB5843497539A74FD0=eris,$50DD343021E509EB3A5A7FD0D8A4F8364AFBDCB5=venus,$253DFF1838A2B7782BE7735F74E50090D46CA1BC=chomsky PURPOSE=GENERAL REASON=FINISHED',

    'CIRC 365 FAILED $E11D2B2269CC25E67CA6C9FB5843497539A74FD0=eris,$50DD343021E509EB3A5A7FD0D8A4F8364AFBDCB5=venus,$253DFF1838A2B7782BE7735F74E50090D46CA1BC=chomsky PURPOSE=GENERAL REASON=TIMEOUT'
    ]

class CircuitTests(unittest.TestCase):

    def test_unlisten(self):
        tor = FakeTorController()
        tor.routers['$E11D2B2269CC25E67CA6C9FB5843497539A74FD0'] = FakeRouter('$E11D2B2269CC25E67CA6C9FB5843497539A74FD0','a')
        
        circuit = Circuit(tor)
        circuit.listen(tor)
        circuit.update('1 LAUNCHED PURPOSE=GENERAL'.split())
        circuit.unlisten(tor)
        circuit.update('1 EXTENDED $E11D2B2269CC25E67CA6C9FB5843497539A74FD0=eris PURPOSE=GENERAL'.split())
        self.assertTrue(len(tor.circuits) == 1)
        self.assertTrue(tor.circuits.has_key(1))
        self.assertTrue(len(tor.extend) == 0)
        
    def test_wrong_update(self):
        tor = FakeTorController()
        circuit = Circuit(tor)
        circuit.listen(tor)
        circuit.update('1 LAUNCHED PURPOSE=GENERAL'.split())
        self.assertRaises(Exception, circuit.update, '2 LAUNCHED PURPOSE=GENERAL'.split())

    def test_closed_remaining_streams(self):
        tor = FakeTorController()
        circuit = Circuit(tor)
        circuit.listen(tor)
        circuit.update('1 LAUNCHED PURPOSE=GENERAL'.split())
        stream = Stream(tor)
        stream.update("1 NEW 0 94.23.164.42.$43ED8310EB968746970896E8835C2F1991E50B69.exit:9001 SOURCE_ADDR=(Tor_internal):0 PURPOSE=DIR_FETCH".split())
        circuit.streams.append(stream)
        self.assertTrue(len(circuit.streams) == 1)

        circuit.update('1 CLOSED $E11D2B2269CC25E67CA6C9FB5843497539A74FD0=eris,$50DD343021E509EB3A5A7FD0D8A4F8364AFBDCB5=venus,$253DFF1838A2B7782BE7735F74E50090D46CA1BC=chomsky PURPOSE=GENERAL REASON=FINISHED'.split())
        circuit.update('1 FAILED $E11D2B2269CC25E67CA6C9FB5843497539A74FD0=eris,$50DD343021E509EB3A5A7FD0D8A4F8364AFBDCB5=venus,$253DFF1838A2B7782BE7735F74E50090D46CA1BC=chomsky PURPOSE=GENERAL REASON=TIMEOUT'.split())
        errs = self.flushLoggedErrors()
        self.assertTrue(len(errs) == 2)
        
    def test_updates(self):
        tor = FakeTorController()
        circuit = Circuit(tor)
        circuit.listen(tor)
        tor.routers['$E11D2B2269CC25E67CA6C9FB5843497539A74FD0'] = FakeRouter('$E11D2B2269CC25E67CA6C9FB5843497539A74FD0','a')
        tor.routers['$50DD343021E509EB3A5A7FD0D8A4F8364AFBDCB5'] = FakeRouter('$50DD343021E509EB3A5A7FD0D8A4F8364AFBDCB5','b')
        tor.routers['$253DFF1838A2B7782BE7735F74E50090D46CA1BC'] = FakeRouter('$253DFF1838A2B7782BE7735F74E50090D46CA1BC','c')

        for ex in examples[:-1]:
            circuit.update(ex.split()[1:])
            self.assertTrue(circuit.state == ex.split()[2])
            self.assertTrue(circuit.purpose == 'GENERAL')

            if '$' in ex:
                self.assertTrue(len(circuit.path) == len(ex.split()[3].split(',')))
                for (r,p) in zip(ex.split()[3].split(','), circuit.path):
                    d = r.split('=')[0]
                    self.assertTrue(d == p.hash)

    def test_extend_messages(self):
        tor = FakeTorController()
        a = FakeRouter('$E11D2B2269CC25E67CA6C9FB5843497539A74FD0','a')
        b = FakeRouter('$50DD343021E509EB3A5A7FD0D8A4F8364AFBDCB5','b')
        c = FakeRouter('$253DFF1838A2B7782BE7735F74E50090D46CA1BC','c')
        tor.routers['$E11D2B2269CC25E67CA6C9FB5843497539A74FD0'] = a
        tor.routers['$50DD343021E509EB3A5A7FD0D8A4F8364AFBDCB5'] = b
        tor.routers['$253DFF1838A2B7782BE7735F74E50090D46CA1BC'] = c
        
        circuit = Circuit(tor)
        circuit.listen(tor)

        circuit.update('365 LAUNCHED PURPOSE=GENERAL'.split())
        self.assertTrue(tor.extend == [])
        circuit.update('365 EXTENDED $E11D2B2269CC25E67CA6C9FB5843497539A74FD0=eris PURPOSE=GENERAL'.split())
        self.assertTrue(len(tor.extend) == 1)
        self.assertTrue(tor.extend[0] == (circuit, a))
        
        circuit.update('365 EXTENDED $E11D2B2269CC25E67CA6C9FB5843497539A74FD0=eris,$50DD343021E509EB3A5A7FD0D8A4F8364AFBDCB5=venus PURPOSE=GENERAL'.split())
        self.assertTrue(len(tor.extend) == 2)
        self.assertTrue(tor.extend[0] == (circuit, a))
        self.assertTrue(tor.extend[1] == (circuit, b))
        
        circuit.update('365 EXTENDED $E11D2B2269CC25E67CA6C9FB5843497539A74FD0=eris,$50DD343021E509EB3A5A7FD0D8A4F8364AFBDCB5=venus,$253DFF1838A2B7782BE7735F74E50090D46CA1BC=chomsky PURPOSE=GENERAL'.split())
        self.assertTrue(len(tor.extend) == 3)
        self.assertTrue(tor.extend[0] == (circuit, a))
        self.assertTrue(tor.extend[1] == (circuit, b))
        self.assertTrue(tor.extend[2] == (circuit, c))

    def test_str(self):
        tor = FakeTorController()
        circuit = Circuit(tor)
        circuit.id = 1
        foo = str(circuit)

    def test_failed_reason(self):
        tor = FakeTorController()
        circuit = Circuit(tor)
        circuit.listen(tor)
        circuit.update('1 FAILED $E11D2B2269CC25E67CA6C9FB5843497539A74FD0=eris PURPOSE=GENERAL REASON=TIMEOUT'.split())
        self.assertTrue(len(tor.failed) == 1)
        self.assertTrue(tor.failed[0] == (circuit, 'TIMEOUT'))
