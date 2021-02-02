import java.math.BigInteger;
import java.security.MessageDigest;

// generate base 10 hash required for ctp config files, as per
// https://github.com/johnperry/Util/blob/master/source/java/org/rsna/util/DigestUtil.java#L91
//
public class PwdHash {
    public static void main(String[] args) throws Exception {
        String test_pwd_1 = "password";
        String test_hash_1 = "126680608771750945340162210354335764377";
        String test_pwd_2 = "aenahM.a6";
        String test_hash_2 = "184893587612723898824540636757540118821";
        String test_pwd_3 = "jooQu-aih6";
        String test_hash_3 = "876824510078208443626133726286448542";
        String string = null;
        if ( args.length > 0 ) {
            string = args[0];
        } else {
            string = test_pwd_1;
        }
        MessageDigest messageDigest = MessageDigest.getInstance("MD5");
        byte[] hashed = messageDigest.digest(string.getBytes("UTF-8"));
        BigInteger bi = new BigInteger(1,hashed);
        String hash = bi.toString();
        System.out.println("String:    " + string);
        System.out.println("Hash:      " + hash);
        if ( string.equals(test_pwd_1) ) {
            System.out.println("True hash: " + test_hash_1);
        }
        if ( string.equals(test_pwd_2) ) {
            System.out.println("True hash: " + test_hash_2);
        }
        if ( string.equals(test_pwd_3) ) {
            System.out.println("True hash: " + test_hash_3);
        }
    }
}
