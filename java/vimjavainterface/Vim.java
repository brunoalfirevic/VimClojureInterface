package vimjavainterface;

public class Vim {
    private static native String nativeEval(String expression);
    private static native void nativeCommand(String command);

    public static Object eval(String expression) {
        return VimSerializer.deserializeFromVimScript(nativeEval(expression));
    }

    public static void command(String command) {
        nativeCommand(command);
    }
}
