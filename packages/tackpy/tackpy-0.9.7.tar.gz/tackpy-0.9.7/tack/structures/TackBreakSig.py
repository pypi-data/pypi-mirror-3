# Authors: 
#   Trevor Perrin
#   Moxie Marlinspike
#
# See the LICENSE file for legal information regarding use of this file.

from tack.crypto.ECPublicKey import ECPublicKey
from tack.tls.TlsStructure import TlsStructure
from tack.tls.TlsStructureWriter import TlsStructureWriter
from tack.util.PEMDecoder import PEMDecoder
from tack.util.PEMEncoder import PEMEncoder

class TackBreakSig(TlsStructure):
    LENGTH = 128

    def __init__(self, data=None):
        if data is None:
            return

        TlsStructure.__init__(self, data)
        if len(data) != TackBreakSig.LENGTH:
            raise SyntaxError("Break signature is the wrong size. Is %s and should be %s." % (len(data), TackBreakSig.LENGTH))

        self.public_key = ECPublicKey.create(self.getBytes(64))
        self.signature  = self.getBytes(64)
            
        if not self.verifySignature():
            raise SyntaxError("TACK_Break_Sig has bad signature")


    @classmethod
    def createFromPem(cls, data):
        return cls(PEMDecoder(data).decode("TACK BREAK SIG"))

    @classmethod
    def createFromPemList(cls, data):
        """Parse a string containing a sequence of PEM Break Sigs.

        Raise a SyntaxError if input is malformed.
        """
        breakSigs = []
        bList = PEMDecoder(data).decodeList("TACK BREAK SIG")
        for b in bList:
            breakSigs.append(TackBreakSig(b))

        return breakSigs

    @classmethod
    def create(cls, public_key, private_key):
        tackBreakSig            = cls()
        tackBreakSig.public_key = public_key
        tackBreakSig.signature  = private_key.sign(bytearray("tack_break_sig", "ascii"))

        return tackBreakSig

    def serialize(self):
        """Return a bytearray containing the TACK_Break_Sig."""
        w = TlsStructureWriter(TackBreakSig.LENGTH)
        w.add(self.public_key.getRawKey(), 64)
        w.add(self.signature, 64)
        return w.getBytes()

    def serializeAsPem(self):
        return PEMEncoder(self.serialize()).encode("TACK BREAK SIG")

    def getTackId(self):
        return str(self.public_key)

    def verifySignature(self):
        return self.public_key.verify(bytearray("tack_break_sig", "ascii"), self.signature)

    def __str__(self):
        """Return a readable string describing this TACK_Break_Sig.
        Used by the "TACK view" command to display TACK objects."""
        return "Breaks TACK ID = %s\n" % self.getTackId()
