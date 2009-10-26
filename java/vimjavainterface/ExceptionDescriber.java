package vimjavainterface;

import java.io.PrintWriter;
import java.io.StringWriter;

public class ExceptionDescriber {
    public static String describe(Throwable throwable) {
        StringWriter sw = new StringWriter();
        throwable.printStackTrace(new PrintWriter(sw, true));
        return sw.toString();
    }
}
