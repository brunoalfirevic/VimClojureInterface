/**
 *   Copyright (c) Bruno Alfirevic. All rights reserved.
 *   The use and distribution terms for this software are covered by the
 *   Eclipse Public License 1.0 (http://opensource.org/licenses/eclipse-1.0.php)
 *   which can be found in the file epl-v10.html at the root of this distribution.
 *   By using this software in any fashion, you are agreeing to be bound by
 *   the terms of this license.
 *   You must not remove this notice, or any other, from this software.
 **/

package vimjavainterface;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.PrintStream;
import java.io.UnsupportedEncodingException;
import java.nio.ByteBuffer;
import java.nio.charset.Charset;

public class StreamCaptor {

    private static boolean outputStreamsCaptured = false;

    public static synchronized void capturetOutputStreams() throws UnsupportedEncodingException {
        if (outputStreamsCaptured)
            return;

        System.setOut(createPrintStream(System.out, new FlushListener() {

            @Override
            public void onFlush(String content) {
                Vim.onOutput(content);
            }
        }));

        System.setErr(createPrintStream(System.err, new FlushListener() {

            @Override
            public void onFlush(String content) {
                Vim.onErr(content);
            }
        }));

        outputStreamsCaptured = true;
    }

    private static PrintStream createPrintStream(PrintStream delegate, FlushListener flushListener) throws UnsupportedEncodingException {
        return new PrintStream(new DelegatingOutputStream(delegate, flushListener, "UTF8"), true, "UTF8");
    }

    static class DelegatingOutputStream extends ByteArrayOutputStream {
        private PrintStream out;
        private FlushListener flushListener;
        private Charset charset;

        private DelegatingOutputStream(PrintStream out, FlushListener flushListener, String charsetName) {
            this.out = out;
            this.flushListener = flushListener;
            this.charset = Charset.forName(charsetName);
        }

        @Override
        public synchronized void flush() throws IOException {
            writeTo(out);
            flushListener.onFlush(charset.decode(ByteBuffer.wrap(toByteArray())).toString());
            reset();
        }
    }

    interface FlushListener {
        void onFlush(String content);
    }
}
