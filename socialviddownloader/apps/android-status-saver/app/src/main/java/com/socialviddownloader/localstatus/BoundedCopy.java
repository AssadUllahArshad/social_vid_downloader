package com.socialviddownloader.localstatus;

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.function.BooleanSupplier;

/** Streaming copy/hash shared with verification; never loads the whole file. */
final class BoundedCopy {
    static final long MAX_BYTES = 200L * 1024 * 1024;
    record Result(long bytes, byte[] digest) {}

    static Result transfer(InputStream input, OutputStream output, long limit,
                           BooleanSupplier cancelled) throws IOException {
        if (input == null) throw new IOException("File is no longer accessible.");
        MessageDigest digest;
        try { digest = MessageDigest.getInstance("SHA-256"); }
        catch (NoSuchAlgorithmException error) { throw new IOException(error); }
        byte[] buffer = new byte[64 * 1024];
        long total = 0;
        int length;
        while (true) {
            if (cancelled.getAsBoolean() || Thread.currentThread().isInterrupted())
                throw new IOException("Copy cancelled.");
            length = input.read(buffer);
            if (length < 0) break;
            if (length == 0) continue;
            if (total > limit - length) throw new IOException("File exceeds the 200 MiB limit.");
            total += length;
            digest.update(buffer, 0, length);
            if (output != null) output.write(buffer, 0, length);
        }
        if (total == 0) throw new IOException("File is empty or no longer available.");
        if (output != null) output.flush();
        return new Result(total, digest.digest());
    }
}
