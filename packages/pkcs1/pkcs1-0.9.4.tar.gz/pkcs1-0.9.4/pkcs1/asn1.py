from pyasn1.type import univ, namedtype, namedval, constraint

MAX = 100

pkcs1 = univ.ObjectIdentifier((1,2,840,113549,1,1,0,1))

rsaEncryption = pkcs1 + univ.ObjectIdentifier((1,))

id_RSAES_OAEP = pkcs1 + univ.ObjectIdentifier((7,))

id_pSpecified = pkcs1 + univ.ObjectIdentifier((9,))

id_RSASSA_PSS = pkcs1 + univ.ObjectIdentifier((10))

md2WithRSAEncrypt = pkcs1 + univ.ObjectIdentifier((2,))
md5WithRSAEncrypt = pkcs1 + univ.ObjectIdentifier((4,))
sha1WithRSAEncrypt = pkcs1 + univ.ObjectIdentifier((5,))
sha256WithRSAEncrypt = pkcs1 + univ.ObjectIdentifier((11,))
sha384WithRSAEncrypt = pkcs1 + univ.ObjectIdentifier((12,))
sha512WithRSAEncrypt = pkcs1 + univ.ObjectIdentifier((13,))

id_sha1 = univ.ObjectIdentifier((1,3,14,3,2,26))

id_md2 = univ.ObjectIdentifier((1,2,840,113549,2,2))
id_md5 = univ.ObjectIdentifier((1,2,840,113549,2,5))

id_mgf1 = pkcs1 + univ.ObjectIdentifier((8,))

class RsaPublicKey(univ.Sequence):
    componentType = namedtype.NamedTypes(
            namedtype.NamedType('modulus', univ.Integer()),
            namedtype.NamedType('publicExponent', univ.Integer()))

class OtherPrimeInfo(univ.Sequence):
    componentType = namedtype.NamedTypes(
            namedtype.NamedType('prime', univ.Integer()),
            namedtype.NamedType('exponent', univ.Integer()),
            namedtype.NamedType('coefficient', univ.Integer()))

class OtherPrimeInfos(univ.SequenceOf):
    componentType = OtherPrimeInfo
    sizeSpec = univ.SequenceOf.sizeSpec + constraint.ValueSizeConstraint(1, MAX)

class Version(univ.Integer):
    namedValues = namedval.NamedValues(
            ('two-prime', 0),
            ('multi', 1))


class RsaPrivateKey(univ.Sequence):
    componentType = namedtype.NamedTypes(
            namedtype.NamedType('version', Version()),
            namedtype.NamedType('modulus', univ.Integer()),
            namedtype.NamedType('publicExponent', univ.Integer()),
            namedtype.NamedType('prime1', univ.Integer()),
            namedtype.NamedType('prime2', univ.Integer()),
            namedtype.NamedType('exponent1', univ.Integer()),
            namedtype.NamedType('exponent2', univ.Integer()),
            namedtype.NamedType('coefficient', univ.Integer()),
            namedtype.NamedType('coefficient', univ.Integer()),
            namedtype.OptionalNamedType('otherPrimeInfos', OtherPrimeInfos()))


class AlgorithmIdentifier(univ.Sequence):
    componentType = namedtype.NamedTypes(
            namedtype.NamedType('algorithm', univ.ObjectIdentifier()),
            namedtype.NamedType('params', univ.Any()))



class DigestInfo(univ.Sequence):
    componentType = namedtype.NamedTypes(
            namedtype.NamedType('digestAlgorithm', AlgorithmIdentifier()),
            namedtype.NamedType('digest', univ.OctetString()))
