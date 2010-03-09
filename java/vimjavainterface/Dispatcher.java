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

import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.util.Collection;

public class Dispatcher {
    public static String dispatch(String targetClassName, String targetMethodName, String args)
            throws ClassNotFoundException, NoSuchMethodException, IllegalAccessException, InvocationTargetException {

        Collection parameters = (Collection)VimSerializer.deserializeFromVimScript(args);
        Object result = dispatchByClassAndMethodName(targetClassName, targetMethodName, parameters);
        return VimSerializer.serializeForVimScript(result);
    }

    public static String dispatchInBackground(final String targetClassName, final String targetMethodName, final String args) {
        new Thread(new Runnable() {
            @Override
            public void run() {
                try
                {
                    dispatch(targetClassName, targetMethodName, args);
                }
                catch(Exception ex)
                {
                    throw new RuntimeException(ex);
                }
            }}).start();

            return VimSerializer.serializeForVimScript(null);
    }

    private static Object dispatchByClassAndMethodName(String targetClassName, String targetMethodName, Collection parameters)
            throws ClassNotFoundException, NoSuchMethodException, IllegalAccessException, InvocationTargetException {

        for(Method method : Class.forName(targetClassName).getMethods()) {
            if (targetMethodName.equals(method.getName()) && method.getParameterTypes().length == parameters.size())
                return method.invoke(null, parameters.toArray());
        }

        throw new NoSuchMethodException(targetMethodName);
    }
}
