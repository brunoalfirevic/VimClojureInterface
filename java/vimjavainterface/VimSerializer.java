package vimjavainterface;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.Hashtable;
import java.util.Map;

class VimSerializer {
    private static final String NULL_TOKEN = "function('IsNull')";

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

            case 'f': { //function('IsNull')
                assert value.substring(position.currentPosition(), position.currentPosition() + NULL_TOKEN.length()).equals(NULL_TOKEN);
                position.skipCount(NULL_TOKEN.length());
                return null;
            }
            
            default: {
                int numberStart = position.currentPosition();
                position.skipUntilEndOfNumber();
                String numberStr = value.substring(numberStart, position.currentPosition() + 1);
                position.skipOne();
                
                if (numberStr.contains("."))
                    return Float.parseFloat(numberStr);

                return Integer.parseInt(numberStr);
            }
        }
    }

    private static void serializeForVimScript(StringBuilder sb, Object value) {
        if (value == null) {
            sb.append(NULL_TOKEN);
        } else if (value instanceof Number) {
            sb.append(value.toString());
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

                if (key == null || key instanceof Collection || key instanceof Map)
                    throw new IllegalArgumentException("Keys in dictionary cannot be collections, maps or null values");

                serializeForVimScript(sb, key);
                sb.append(':');
                serializeForVimScript(sb, map.get(key));
                isFirst = false;
            }
            sb.append('}');
        } else {
            sb.append("'" + (value.toString()).replace("'", "''") + "'");
        }
    }

    static class ParsingPosition {
        private String value;
        private int position;

        public ParsingPosition(String value) {
            this.value = value;
        }

        public void skipOne() {
            skipCount(1);
        }

        public void skipCount(int charCount) {
            position += charCount;
        }

        public char current() {
            return value.charAt(position);
        }

        public int currentPosition() {
            return position;
        }

        public void skip(Character... characters) {
            while (position < value.length() && (Character.isWhitespace(current())
                    || Arrays.asList(characters).contains(current())))
                skipOne();
        }

        public void skipUntilEndOfNumber() {
            while (position + 1 < value.length() && (Character.isDigit(value.charAt(position + 1))
                    || value.charAt(position + 1) == '.'))
                position++;
        }

        private void skipUntilEndOfString() {
            while(true) {
                if (current() == '\'') {
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
