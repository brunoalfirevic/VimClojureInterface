package vimjavainterface;

import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.util.Arrays;
import java.util.Collection;
import java.util.List;
import java.util.Map;

public class Vim {
    public static native String eval(String serializationFunction, String expression);
    public static native void command(String command);

    public static String dispatch(String target, String dispatcher, String deserializer, String arg)
            throws ClassNotFoundException, NoSuchMethodException, IllegalAccessException, InvocationTargetException {

        Collection parameters = deserializer == null
                ? toList(arg)
                : (Collection)dispatchByClassAndMethodName(deserializer, toList(arg));

        Object result = dispatcher == null 
                ? dispatchByClassAndMethodName(target, parameters)
                : dispatchByClassAndMethodName(dispatcher, toList(target, parameters));
        
        return serializeForVimScript(result);
    }

    public static Object dispatchByClassAndMethodName(String target, Collection parameters)
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

    private static List toList(Object... args) {
        return Arrays.asList(args);
    }

    private static String serializeForVimScript(Object value) {
        StringBuilder sb = new StringBuilder();
        serializeForVimScript(sb, value);
        return sb.toString();
    }

    private static void serializeForVimScript(StringBuilder sb, Object value) {
        if (value == null) {
            sb.append("g:null");
        } else if (value instanceof Number) {
            sb.append(value.toString());
        } else if (value instanceof String) {
            sb.append("'" + ((String)value).replace("'", "''").replace("\r", "\\r").replace("\n", "\\n") + "'");
        } else if (value instanceof Collection) {
            Collection collection = (Collection)value;
            sb.append('[');
            boolean isFirst = true;
            for(Object o : collection) {
                if (!isFirst)
                    sb.append(',');
                serializeForVimScript(sb, o);
                isFirst = false;
            }
            sb.append(']');
        } else if (value instanceof Map) {
            Map map = (Map)value;
            sb.append('{');
            boolean isFirst = true;
            for(Object key : map.keySet()){
                if (!isFirst)
                    sb.append(',');

                if (!(key instanceof Integer
                        || key instanceof Long
                        || key instanceof Byte
                        || key instanceof String))
                    throw new IllegalArgumentException("Only whole numbers and strings can be keys in dictionary");

                serializeForVimScript(sb, key);
                sb.append(':');
                serializeForVimScript(sb, map.get(key));
                isFirst = false;
            }
            sb.append('}');
        } else {
            throw new IllegalArgumentException("Type not supported in Vim Script");
        }
    }
}
