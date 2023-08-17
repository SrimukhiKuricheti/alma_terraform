from ldap3 import Server, Connection, ALL
import netifaces as ni

ip = ni.ifaddresses('eth0')[ni.AF_INET][0]['addr']
print(ip)

# LDAP server configuration
ldap_server = 'ldap://'+ip
ldap_user = 'cn=Manager,dc=srv,dc=world'
ldap_password = 'test123'

# Create LDAP connection
server = Server(ldap_server, get_info=ALL)
conn = Connection(server, user=ldap_user, password=ldap_password)

# Perform LDAP bind operation
if conn.bind():
    print("LDAP connection successful")
    # Continue with additional operations
else:
    print("LDAP connection failed:", conn.result)

# Disconnect from LDAP server
conn.unbind()
