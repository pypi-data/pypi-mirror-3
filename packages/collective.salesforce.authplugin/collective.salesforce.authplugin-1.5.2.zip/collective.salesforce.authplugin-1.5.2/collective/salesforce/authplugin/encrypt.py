# pluggable encryption thanks to SQLPASPlugin

import re
import sha
import md5
from zope import component
from zope import interface
from AccessControl.AuthEncoding import SSHADigestScheme

DEFAULT_ENCRYPTION = 'md5'

_ENCRYPT_METHOD_RE = re.compile(r'^\{([a-zA-Z0-9]*)\}')

def query_encrypter(encrypted_text, default=DEFAULT_ENCRYPTION):
    """Find the encrypter which knows how to handle the same encryption
    that's used for *encrypted_text*.

    Test setup:
      >>> from zope import component
      >>> component.provideUtility(PlainEncrypter(), name='plain')

    Example usage:
      >>> query_encrypter('default').encrypt('hello world')
      '5eb63bbbe01eeed093cb22bb8f5acdc3'

      >>> query_encrypter('default')
      <collective.salesforce.authplugin.encrypt.MD5Encrypter object at ...>

      >>> query_encrypter('{sha}3773dea65156909838fa6c22825cafe090ff8030')
      <collective.salesforce.authplugin.encrypt.SHAEncrypter object at ...>

      >>> query_encrypter('{plain}327b6f07435811239bc47e1544353273')
      <collective.salesforce.authplugin.encrypt.PlainEncrypter object at ...>

      >>> query_encrypter('{foo}boogie') is None
      True
    """
    encrypt_method = default
    m = _ENCRYPT_METHOD_RE.match(encrypted_text)
    if m is not None:
        encrypt_method = m.group(1)
    return find_encrypter(encrypt_method)

def find_encrypter(encrypt_method=DEFAULT_ENCRYPTION):
    """Do a lookup for the encrypter which matches *encrypt_method*.
    """
    encrypter = component.queryUtility(IEncrypter, name=encrypt_method)
    return encrypter


class IEncrypter(interface.Interface):
    """A reusable interface for indicating classes that can encrypt things.
    """
    def encrypt(text):
        """Encrypt the given text.
        """

    def validate(reference, attempt):
        """Validate attempt against reference.
        """
        
    name = interface.Attribute("The name for this IEncrypter")



class PlainEncrypter(object):
    """An IEncrypter implementation for mock encrypting text.

    PlainEncrypter example usage:

      >>> PlainEncrypter().encrypt('foo bar')
      'foo bar'
      >>> PlainEncrypter().validate('foo bar', 'foo bar')
      True

    """
    interface.implements(IEncrypter)

    name = 'plain'

    def encrypt(self, text):
        """Encrypt the given text."""
        return text

    def validate(self, reference, attempt):
        """Validate attempt against reference."""
        return reference == self.encrypt(attempt)
        
    


class SHAEncrypter(PlainEncrypter):
    """An IEncrypter implementation for SHA encrypting text.


    SHAEncrypter example usage:

      >>> SHAEncrypter().encrypt('foo bar')
      '3773dea65156909838fa6c22825cafe090ff8030'
    """
    name = 'sha'

    def encrypt(self, text):
        """Encrypt the given text."""
        return sha.sha(text).hexdigest()



class MD5Encrypter(PlainEncrypter):
    """An IEncrypter implementation for MD5 encrypting text.


    MD5Encrypter example usage:

      >>> MD5Encrypter().encrypt('foo bar')
      '327b6f07435811239bc47e1544353273'
    """
    name = 'md5'

    def encrypt(self, text):
        """Encrypt the given text."""
        return md5.md5(text).hexdigest()


class SSHAEncrypter(PlainEncrypter):
    """An IEncrypter implementation for SSHA Digest.

    Note that SSHA uses salt, so encrypt efforts on
    the same key are unlikely to return the same result.

    SSHAEncrypter example usage:

      >>> SSHAEncrypter().validate('bvwPb9gvx+GkDjTRBhbfVsjrFHs2rUKLcRCO', 'foo bar')
      True
    """
    name = 'ssha'
    
    def encrypt(self, text):
        """Encrypt the given text."""
        return SSHADigestScheme().encrypt(text)

    def validate(self, reference, attempt):
        """Validate attempt against reference."""
        # SSHA uses a salted hash, so simple comparison won't work;
        # fortunately, the scheme provides a validate method that
        # takes this into account
        return SSHADigestScheme().validate(reference, attempt)
