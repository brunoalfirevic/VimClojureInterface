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

    private static Object dispatchByClassAndMethodName(String targetClassName, String targetMethodName, Collection parameters)
            throws ClassNotFoundException, NoSuchMethodException, IllegalAccessException, InvocationTargetException {

        for(Method method : Class.forName(targetClassName).getMethods()) {
            if (targetMethodName.equals(method.getName()) && method.getParameterTypes().length == parameters.size())
                return method.invoke(null, parameters.toArray());
        }

        throw new NoSuchMethodException(targetMethodName);
    }
}
