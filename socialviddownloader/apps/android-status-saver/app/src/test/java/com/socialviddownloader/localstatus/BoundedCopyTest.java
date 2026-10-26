package com.socialviddownloader.localstatus;

import org.junit.Test;
import java.io.*;
import java.security.MessageDigest;
import static org.junit.Assert.*;

public class BoundedCopyTest {
    @Test public void copiesActualBytesAndHashes() throws Exception {
        byte[] source = new byte[5 * 1024 * 1024 + 13];
        new java.util.Random(42).nextBytes(source);
        ByteArrayOutputStream target = new ByteArrayOutputStream();
        var result = BoundedCopy.transfer(new ByteArrayInputStream(source), target, source.length, () -> false);
        assertArrayEquals(source, target.toByteArray());
        assertEquals(source.length, result.bytes());
        assertArrayEquals(MessageDigest.getInstance("SHA-256").digest(source), result.digest());
    }
    @Test public void neverWritesPastLimit() {
        var target = new ByteArrayOutputStream();
        assertThrows(IOException.class, () -> BoundedCopy.transfer(new ByteArrayInputStream(new byte[100]), target, 99, () -> false));
        assertTrue(target.size() <= 99);
    }
    @Test public void cancellationStopsBeforeRead() {
        assertThrows(IOException.class, () -> BoundedCopy.transfer(new ByteArrayInputStream(new byte[]{1}), null, 100, () -> true));
    }
    @Test public void emptyAndMissingAreFailures() {
        assertThrows(IOException.class, () -> BoundedCopy.transfer(new ByteArrayInputStream(new byte[0]), null, 100, () -> false));
        assertThrows(IOException.class, () -> BoundedCopy.transfer(null, null, 100, () -> false));
    }
    @Test public void readFailureCannotReportSuccess() {
        InputStream broken = new InputStream() { public int read() throws IOException { throw new IOException("revoked"); } };
        assertThrows(IOException.class, () -> BoundedCopy.transfer(broken, null, 100, () -> false));
    }
}
