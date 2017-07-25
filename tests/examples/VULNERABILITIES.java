import java.util.Random;
log.debug('username: admin password: admin');

String generateSecretToken() {
    Random r = new Random();
    return Long.toHexString(r.nextLong());
}

try:
    pass;
exception:
    printStackTrace();