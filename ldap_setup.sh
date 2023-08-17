
echo "Executing LDAP Setup"

USER=`whoami`
echo $USER

sudo yum --enablerepo=extras install epel-release -y
sudo sed -i s/enabled=0/enabled=1/ /etc/yum.repos.d/almalinux-powertools.repo

# installing form EPL
sudo  dnf --enablerepo=epel -y install openldap-servers openldap-clients
sudo systemctl enable --now slapd

slappasswd -s test123 | sudo tee -a root_pwd.txt
cat root_pwd.txt


ROOT_HASH=`cat root_pwd.txt`

echo "dn: olcDatabase={0}config,cn=config
changetype: modify
add: olcRootPW
olcRootPW: $ROOT_HASH" >> chrootpw.ldif

sudo ldapadd -Y EXTERNAL -H ldapi:/// -f chrootpw.ldif

# Importing Basic Schemas
sudo ldapadd -Y EXTERNAL -H ldapi:/// -f /etc/openldap/schema/cosine.ldif
sudo ldapadd -Y EXTERNAL -H ldapi:/// -f /etc/openldap/schema/nis.ldif
sudo ldapadd -Y EXTERNAL -H ldapi:/// -f /etc/openldap/schema/inetorgperson.ldif


######## Set Domain Name on LDAP DB ########

# generate directory manager's password

slappasswd -s man123 | sudo tee -a manager_pwd.txt
cat manager_pwd.txt

MAN_HASH=`cat manager_pwd.txt`
echo $MAN_HASH

# replace to your own domain name for [dc=***,dc=***] section
# specify the password generated above for [olcRootPW] section
echo "dn: olcDatabase={1}monitor,cn=config
changetype: modify
replace: olcAccess
olcAccess: {0}to * by dn.base="gidNumber=0+uidNumber=0,cn=peercred,cn=external,cn=auth"
  read by dn.base="cn=Manager,dc=srv,dc=world" read by * none

dn: olcDatabase={2}mdb,cn=config
changetype: modify
replace: olcSuffix
olcSuffix: dc=srv,dc=world

dn: olcDatabase={2}mdb,cn=config
changetype: modify
replace: olcRootDN
olcRootDN: cn=Manager,dc=srv,dc=world

dn: olcDatabase={2}mdb,cn=config
changetype: modify
add: olcRootPW
olcRootPW: $ROOT_HASH

dn: olcDatabase={2}mdb,cn=config
changetype: modify
add: olcAccess
olcAccess: {0}to attrs=userPassword,shadowLastChange by
dn="cn=Manager,dc=srv,dc=world" write by anonymous auth by self write by * none
olcAccess: {1}to dn.base="" by * read
olcAccess: {2}to * by dn="cn=Manager,dc=srv,dc=world" write by * read" >> chdomain.ldif

sudo ldapmodify -Y EXTERNAL -H ldapi:/// -f chdomain.ldif


###### Configuring Base domain #######

# replace to your own domain name for [dc=***,dc=***] section

echo "dn: dc=srv,dc=world
objectClass: top
objectClass: dcObject
objectclass: organization
o: Server World
dc: srv

dn: cn=Manager,dc=srv,dc=world
objectClass: organizationalRole
cn: Manager
description: Directory Manager

dn: ou=People,dc=srv,dc=world
objectClass: organizationalUnit
ou: People

dn: ou=Group,dc=srv,dc=world
objectClass: organizationalUnit
ou: Group" >> basedomain.ldif

ldapadd -x -D cn=Manager,dc=srv,dc=world -w test123 -f basedomain.ldif


echo "Creating Users"
ldapadd -x -D "cn=Manager,dc=srv,dc=world" -w "test123" -f user1.ldif

echo "Creating Groups"
ldapadd -x -D "cn=Manager,dc=srv,dc=world" -w "test123" -f group1.ldif
