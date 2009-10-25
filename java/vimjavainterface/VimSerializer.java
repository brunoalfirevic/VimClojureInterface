package vimjavainterface;

import java.util.Arrays;
import java.util.Collection;
import java.util.Map;

class VimSerializer {
    public static Collection deserializeFromVimScript(String parameters) {
        return Arrays.asList(parameters);
    }

    public static String serializeForVimScript(Object value) {
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
