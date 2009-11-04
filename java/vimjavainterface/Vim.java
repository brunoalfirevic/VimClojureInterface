package vimjavainterface;

public class Vim {
    private static native String nativeEval(String expression);
    private static native void nativeCommand(String command);
    private static native String nativeSafeEval(String expression);
    private static native void nativeSafeCommand(String command);

    public static Object eval(String expression) {
        return VimSerializer.deserializeFromVimScript(nativeEval(expression));
    }

    public static void command(String command) {
        nativeCommand(command);
    }

    public static Object safeEval(String expression) {
        return VimSerializer.deserializeFromVimScript(nativeSafeEval(expression));
    }

    public static void safeCommand(String command) {
        nativeSafeCommand(command);
    }
}
