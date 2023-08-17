import random
import string
from ldap3 import Server, Connection, ALL, MODIFY_ADD

import netifaces as ni

ip = ni.ifaddresses('eth0')[ni.AF_INET][0]['addr']
print(ip)

# LDAP server configuration
ldap_server = 'ldap://'+ip
ldap_user = 'cn=Manager,dc=srv,dc=world'
ldap_password = 'test123'

# Number of users and groups
num_users = 5000
num_groups = 1000

# Generate random usernames and group names
def generate_random_string(length):
    return ''.join(random.choices(string.ascii_lowercase, k=length))

def generate_pwd():
    password = generate_random_string(10)
    # Generate salt
    salt = os.urandom(4)
    # Concatenate password and salt
    salted_password = password.encode() + salt
    # Generate SHA-1 hash
    sha1_hash = hashlib.sha1(salted_password).digest()
    # Concatenate hash and salt
    ssha_hash = sha1_hash + salt
    # Base64 encode the result
    ssha_password_hash = "{SSHA}" + base64.b64encode(ssha_hash).decode()
    print("SSHA password hash:", ssha_password_hash)
    return ssha_password_hash


users = [f'user{i}' for i in range(1, num_users + 1)]
groups = [f'group{i}' for i in range(1, num_groups + 1)]

# Function to create LDAP connection
def get_ldap_connection():
    server = Server(ldap_server, get_info=ALL)
    conn = Connection(server, user=ldap_user, password=ldap_password)
    conn.bind()
    return conn

# Function to create users
def create_users():
    conn = get_ldap_connection()

    for user in users:
        user_dn = f'uid={user},ou=Manager,dc=srv,dc=world'
        user_password = generate_random_string(8)
        user_entry = {
            'objectClass': ['inetOrgPerson'],
            'uid': user,
            'cn': user.capitalize(),
            'sn': user.capitalize(),
            'userPassword': user_password
        }
        conn.add(user_dn, attributes=user_entry)

    conn.unbind()

# Function to create groups and add users to groups
def create_groups_and_add_users():
    conn = get_ldap_connection()

    for i, group in enumerate(groups):
        group_dn = f'cn={group},ou=Group,dc=srv,dc=world'
        start_user = i * 5
        end_user = min(start_user + 4, num_users)
        users_to_add = [f'user{j}' for j in range(start_user + 1, end_user + 1)]
        
        group_entry = {
            'objectClass': ['posixGroup'],
            'cn': group,
            'gidNumber': 1000 + i,
            'memberUid': users_to_add
        }
        conn.add(group_dn, attributes=group_entry)

    conn.unbind()

if __name__ == "__main__":
    create_users()
    create_groups_and_add_users()
