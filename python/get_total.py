from ldap3 import Server, Connection, ALL, SUBTREE

# LDAP server configuration
import netifaces as ni

ip = ni.ifaddresses('eth0')[ni.AF_INET][0]['addr']
print(ip)

# LDAP server configuration
ldap_server = 'ldap://'+ip
ldap_user = 'cn=Manager,dc=srv,dc=world'
ldap_password = 'test123'
base_dn = 'dc=srv,dc=world'  # Adjust the base DN according to your LDAP structure

# Function to create LDAP connection
def get_ldap_connection():
    server = Server(ldap_server, get_info=ALL)
    conn = Connection(server, user=ldap_user, password=ldap_password)
    conn.bind()
    return conn

# Function to get total number of groups
def get_total_groups():
    conn = get_ldap_connection()

    conn.search(search_base=base_dn, search_filter='(objectClass=posixGroup)', search_scope=SUBTREE)
    total_groups = len(conn.entries)

    conn.unbind()
    return total_groups

# Function to get total number of users
def get_total_users():
    conn = get_ldap_connection()

    conn.search(search_base=base_dn, search_filter='(objectClass=inetOrgPerson)', search_scope=SUBTREE)
    total_users = len(conn.entries)

    conn.unbind()
    return total_users

# Function to get number of users per group
def get_users_per_group():
    conn = get_ldap_connection()

    conn.search(search_base=base_dn, search_filter='(objectClass=posixGroup)', search_scope=SUBTREE, attributes=['memberUid'])

    users_per_group = {}
    for entry in conn.entries:
        group = entry.entry_dn.split(',')[0][3:]
        users = entry.memberUid.values if 'memberUid' in entry else []
        users_per_group[group] = len(users)

    conn.unbind()
    return users_per_group

if __name__ == "__main__":
    total_groups = get_total_groups()
    total_users = get_total_users()
    users_per_group = get_users_per_group()

    print(f"Total number of groups: {total_groups}")
    print(f"Total number of users: {total_users}")
    print("Number of users per group:")
    for group, num_users in users_per_group.items():
        print(f"Group {group}: {num_users}")
