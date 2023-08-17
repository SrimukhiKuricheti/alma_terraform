import random
import string

import hashlib
import os
import base64

# Password to be hashed
# password = 'user123'
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


# Number of users and groups
num_users = 5000
num_groups = 1000


users = [f'user{i}' for i in range(1, num_users + 1)]
groups = [f'group{i}' for i in range(1, num_groups + 1)]

# Create LDIF files for users
with open('users.ldif', 'w') as user_ldif:
    for user in users:
        user_ldif.write(f'dn: uid={user},ou=People,dc=srv,dc=world\n')
        user_ldif.write('objectClass: inetOrgPerson\n')
        user_ldif.write(f'uid: {user}\n')
        user_ldif.write(f'cn: {user.capitalize()}\n')
        user_ldif.write(f'sn: {user.capitalize()}\n')
        user_ldif.write(f'userPassword: {generate_pwd()}\n\n')

# Create LDIF files for groups
with open('groups.ldif', 'w') as group_ldif:
    for i, group in enumerate(groups):
        group_ldif.write(f'dn: cn={group},ou=Group,dc=srv,dc=world\n')
        group_ldif.write('objectClass: posixGroup\n')
        group_ldif.write(f'cn: {group}\n')
        group_ldif.write(f'gidNumber: {1000 + i}\n')
        start_user = i * 5 + 1
        end_user = min(start_user + 4, num_users)
        group_ldif.write('memberUid: ')
        for user_num in range(start_user, end_user + 1):
            group_ldif.write(f'user{user_num} ')
        group_ldif.write('\n\n')
        
        
