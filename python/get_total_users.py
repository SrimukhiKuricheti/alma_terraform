from ldap3 import Server, Connection, ALL, SUBTREE

import netifaces as ni

ip = ni.ifaddresses('eth0')[ni.AF_INET][0]['addr']
print(ip)

# LDAP server configuration
ldap_server = 'ldap://'+ip
ldap_user = 'cn=Manager,dc=srv,dc=world'
ldap_password = 'test123'
base_dn = 'ou=Manager,dc=srv,dc=world'  # Adjust the base DN according to your LDAP structure

# Function to create LDAP connection
def get_ldap_connection():
    server = Server(ldap_server, get_info=ALL)
    conn = Connection(server, user=ldap_user, password=ldap_password)
    conn.bind()
    return conn

# Function to get total number of users
def get_total_users():
    conn = get_ldap_connection()

    conn.search(search_base=base_dn, search_filter='(objectClass=inetOrgPerson)', search_scope=SUBTREE)
    total_users = len(conn.entries)

    conn.unbind()
    return total_users

if __name__ == "__main__":
    total_users = get_total_users()
    print(f"Total number of users: {total_users}")
