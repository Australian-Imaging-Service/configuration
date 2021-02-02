import hashlib, sys

# generate base 10 hash required for ctp config files, as per
# https://github.com/johnperry/Util/blob/master/source/java/org/rsna/util/DigestUtil.java#L91

test_pwd_1 = 'password';
test_hash_1 = '126680608771750945340162210354335764377';
test_pwd_2 = 'aenahM.a6';
test_hash_2 = '184893587612723898824540636757540118821';
test_pwd_3 = 'jooQu-aih6';
test_hash_3 = '876824510078208443626133726286448542';
string = None;

if len(sys.argv) > 1:
    string = sys.argv[1];
else:
    string = test_pwd_1;

hexhash = hashlib.md5(string.encode('utf-8')).hexdigest()
ctphash = str(int(hexhash, 16))
print('String:    ' + string);
print('Hash:      ' + ctphash);

if string == test_pwd_1:
    print('True hash: ' + test_hash_1);
if string == test_pwd_2:
    print('True hash: ' + test_hash_2);
if string == test_pwd_3:
    print('True hash: ' + test_hash_3);
