import java.util.Random;

# CVI-190001
log.debug('username: admin password: admin');

# CVI-200001
String generateSecretToken() {
    Random r = new Random();
    return Long.toHexString(r.nextLong());
}

try:
    # CVI-330001
    Cipher c = Cipher.getInstance("DESede/CBC/PKCS5Padding");
    c.init(Cipher.ENCRYPT_MODE, k, iv);
    byte[] cipherText = c.doFinal(plainText);

    # CVI-330002
    Cipher c = Cipher.getInstance("AES/ECB/NoPadding");
    c.init(Cipher.ENCRYPT_MODE, k, iv);
    byte[] cipherText = c.doFinal(plainText);
exception:
    # CVI-190002
    printStackTrace();

# CVI-110005
class TrustAllManager implements X509TrustManager {

    @Override
    public void checkClientTrusted(X509Certificate[] x509Certificates, String s) throws CertificateException {
        //Trust any client connecting (no certificate validation)
    }

    @Override
    public void checkServerTrusted(X509Certificate[] x509Certificates, String s) throws CertificateException {
        //Trust any remote server (no certificate validation)
    }

    @Override
    public X509Certificate[] getAcceptedIssuers() {
        return null;
    }
}

# CVI-140002
out.println(request.getParameter("test"))

# CVI-160001
String hql = "select max(detailLineNo) from TWmsSoreturnAsnDetailEntity where isDel = 0 and asnId="+headId;

# CVI-110003
String url = "http://www.google.com"
String url2 = "http://www.mogujie.com"
