package vimjavainterface;

import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.util.Arrays;
import java.util.Collection;

public class Dispatcher {
    public static String dispatch(String target, String dispatcher, String args)
            throws ClassNotFoundException, NoSuchMethodException, IllegalAccessException, InvocationTargetException {

        Collection parameters = (Collection)VimSerializer.deserializeFromVimScript(args);

        Object result = dispatcher == null
                ? dispatchByClassAndMethodName(target, parameters)
                : dispatchByClassAndMethodName(dispatcher, Arrays.asList(target, parameters));

        return VimSerializer.serializeForVimScript(result);
    }

    private static Object dispatchByClassAndMethodName(String target, Collection parameters)
            throws ClassNotFoundException, NoSuchMethodException, IllegalAccessException, InvocationTargetException {

        if (!target.contains("/"))
            throw new IllegalArgumentException("Target must be in format {package.class}/{method}");

        String targetClassName = target.split("/", 2)[0];
        String targetMethodName = target.split("/", 2)[1];

        for(Method method : Class.forName(targetClassName).getMethods()) {
            if (targetMethodName.equals(method.getName()) && method.getParameterTypes().length == parameters.size())
                return method.invoke(null, parameters.toArray());
        }

        throw new NoSuchMethodException(targetMethodName);
    }
}
