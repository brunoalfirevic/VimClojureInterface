package vimjavainterface;

import java.util.ArrayList;
import java.util.Collection;
import java.util.Hashtable;
import java.util.Map;

class VimSerializer {
    public static Object deserializeFromVimScript(String value) {
        return deserializeFromVimScript(value, new ParsingPosition(value));
    }

    public static String serializeForVimScript(Object value) {
        StringBuilder sb = new StringBuilder();
        serializeForVimScript(sb, value);
        return sb.toString();
    }

    private static Object deserializeFromVimScript(String value, ParsingPosition position) {
        position.skip();

        switch(position.current())
        {
            case '[': {
                position.skipOne();
                position.skip();

                ArrayList result = new ArrayList();
                while (position.current() != ']') {
                    Object listElement = deserializeFromVimScript(value, position);
                    result.add(listElement);
                    position.skip(',');
                }
                position.skipOne();
                return result;
            }
            
            case '{': {
                position.skipOne();
                position.skip();

                Hashtable result = new Hashtable();
                while (position.current() != '}') {
                    Object mapKey = deserializeFromVimScript(value, position);
                    position.skip(':');
                    Object mapValue = deserializeFromVimScript(value, position);
                    result.put(mapKey, mapValue);

                    position.skip(',');
                }
                position.skipOne();
                return result;
            }
            
            case '\'': {
                position.skipOne();
                
                int stringStart = position.currentPosition();
                position.skipUntilEndOfString();
                String result = value.substring(stringStart, position.currentPosition()).replace("''", "'");

                position.skipOne();
                return result;
            }
            
            default: {
                int numberStart = position.currentPosition();
                position.skipUntilEndOfNumber();
                String numberStr = value.substring(numberStart, position.currentPosition());

                if (numberStr.contains("."))
                    return Float.parseFloat(numberStr);

                return Integer.parseInt(numberStr);
            }
        }
    }

    private static void serializeForVimScript(StringBuilder sb, Object value) {
        if (value == null) {
            sb.append("g:null");
        } else if (value instanceof Number) {
            sb.append(value.toString());
        } else if (value instanceof String) {
            sb.append("'" + ((String)value).replace("'", "''") + "'");
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

    static class ParsingPosition
    {
        private String value;
        private int position;

        public ParsingPosition(String value)
        {
            this.value = value;
        }

        public void skipOne()
        {
            position++;
        }

        public char current()
        {
            return value.charAt(position);
        }

        public int currentPosition()
        {
            return position;
        }

        public void skip(char... characters)
        {
            while (position < value.length() && Character.isWhitespace(value.charAt(position)))
                position++;
        }

        public void skipUntilEndOfNumber()
        {
            while (position < value.length() && (Character.isDigit(value.charAt(position)) || value.charAt(position) == '.'))
                position++;
        }

        private void skipUntilEndOfString() {
            while(true) {
                if (value.charAt(position) == '\'') {
                  if (position != value.length() - 1 && value.charAt(position + 1) == '\'')
                      position += 2;
                  else
                      break;
                } else {
                    position++;
                }
            }
        }
    }
}
