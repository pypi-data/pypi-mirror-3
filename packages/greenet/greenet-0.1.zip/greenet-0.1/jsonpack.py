"""
A json-dict format message-stream unpack tool, based on cjson.
"""
import cjson as json

__all__ = ['decode', 'encode', 'Unpacker', 'json']


def encode(msg):
    assert isinstance(msg, dict)
    return json.encode(msg)

def decode(data):
    msg = json.decode(data)
    assert isinstance(msg, dict)
    return msg

#decode = json.decode
#encode = json.encode

class Unpacker:
    
    def __init__(self, bufsize=4096):
        """
        @param bufsize: no limit if bufsize<=0
        """
        self.buf = ''
        self.bufsize = bufsize
    
    def feed(self, data):
        self.buf += data
        if not self.buf: return []
        
        paks = self.buf.split('}{')
        pn = len(paks)
        msgs = []
        
        if pn > 1:
            self.buf = '{' + paks[-1]
            paks = paks[:-1]
            for i, s in enumerate(paks):
                if not s: continue
                if s[0] != '{': s = '{' + s
                if s[-1] != '}': s += '}'
                try: msg = json.decode(s)
                except: continue
                msgs.append(msg)
        
        del paks, pn
        
        if self.buf:
            if self.buf[-1] != '}':
                if self.bufsize>0 and len(self.buf) > self.bufsize:
                    print 'Warning: JsonUnpacker oversize %d.' % MSG_SIZE_LIMIT
                    print 'Buffer:', self.buf[:200]
                    self.clear()
                return msgs
            try: msg = json.decode(self.buf)
            except: return msgs
            msgs.append(msg)
            self.clear()
        
        return msgs

    def clear(self):
        self.buf = ''

