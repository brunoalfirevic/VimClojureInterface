package vimjavainterface;

public class Vim {
    private static native String _eval(String expression);
    private static native void _command(String command);

    public static Object eval(String expression) {
        return VimSerializer.deserializeFromVimScript(_eval(expression));
    }

    public static void command(String command) {
        _command(command);
    }
}
