import ldap3
#import netifaces as ni

#ip = ni.ifaddresses('eth0')[ni.AF_INET][0]['addr']
#print(ip)

ip = '192.168.122.153:389'
# LDAP server configuration
ldap_server = ip
ldap_user = 'cn=Manager,dc=srv,dc=world'
ldap_password = 'test123'
# LDAP search filter
search_base = 'ou=People,dc=srv,dc=world'
search_filter = '(objectClass=inetOrgPerson)'
attributes = ['cn', 'uid', 'givenName', 'sn', 'mail']

# Create LDAP connection
server = ldap3.Server(ldap_server, get_info=ldap3.ALL)
conn = ldap3.Connection(server, user=ldap_user, password=ldap_password)

# Perform LDAP bind operation
conn.bind()

# Perform LDAP search
conn.search(search_base, search_filter, attributes=attributes, search_scope=ldap3.SUBTREE)

# Get search results
users = conn.entries

# Process and print user information
for user in users:
    print("User CN:", user.cn)
    print("User UID:", user.uid)
    print("User Last Name:", user.sn)
    print("-----------")

# Disconnect from LDAP server
conn.unbind()
