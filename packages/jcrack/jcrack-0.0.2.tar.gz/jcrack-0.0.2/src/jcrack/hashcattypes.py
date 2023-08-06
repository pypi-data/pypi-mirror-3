
def GetHashcatMaps():

    inv_map = {
        0 : 'MD5',
       10 : 'md5($pass.$salt)',
       11 : 'Joomla',
      100 : 'SHA1',
      101 : 'nsldap, SHA-1(Base64), Netscape LDAP SHA',
      110 : 'sha1($pass.$salt)',
      111 : 'nsldaps, SSHA-1(Base64), Netscape LDAP SSHA',
      112 : 'Oracle 11g',
      131 : 'MSSQL(2000)',
      132 : 'MSSQL(2005)',
      300 : 'MySQL',
      900 : 'MD4',
     1000 : 'NTLM',
     1100 : 'Domain Cached Credentials, mscash',
     1400 : 'SHA256',
     1500 : 'descrypt, DES(Unix), Traditional DES',
     1900 : 'SL3',
     2400 : 'Cisco-PIX MD5',
     2600 : 'md5(md5($pass))',
     2611 : 'vBulletin < v3.8.5',
     2711 : 'vBulletin > v3.8.5',
     2811 : 'IPB2+, MyBB1.2+',
     3000 : 'LM',
    }

    map = dict((v,k) for k,v in inv_map.iteritems())

    return (map, inv_map)
