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

public class Vim {
    private static native String nativeEval(String expression);
    private static native void nativeCommand(String command);
    private static native String nativeSafeEval(String expression);
    private static native void nativeSafeCommand(String command);
    private static native void nativeOnOutput(String content);
    private static native void nativeOnErr(String content);

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

    public static void onOutput(String content) {
        nativeOnOutput(content);
    }

    public static void onErr(String content) {
        nativeOnErr(content);
    }
}
