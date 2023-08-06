"""
Utility functions and classes.
"""
import re
import logging

from stompclient.frame import Frame, VALID_COMMANDS

__authors__ = ['"Hans Lellelid" <hans@xmpl.org>', 'Ricky Iacovou (stomper)']
__copyright__ = "Copyright 2010 Hans Lellelid"
__license__ = """Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
 
  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License."""

class FrameBuffer(object):
    """
    A customized version of the StompBuffer class from Stomper project that returns frame objects
    and supports iteration.
    
    This version of the parser also assumes that stomp messages with no content-lengh
    end in a simple \\x00 char, not \\x00\\n as is assumed by
    C{stomper.stompbuffer.StompBuffer}. Additionally, this class differs from Stomper version 
    by conforming to PEP-8 coding style.
    
    This class can be used to smooth over a transport that may provide partial frames (or
    may provide multiple frames in one data buffer).
    
    @ivar buffer: The internal byte buffer.
    @type buffer: C{str}
    
    @ivar debug: Log extra parsing debug (logs will be DEBUG level). 
    @type debug: C{bool} 
    """
        
    # regexp to check that the buffer starts with a command.
    command_re = re.compile('^(.+?)\n')
    
    # regexp to remove everything up to and including the first
    # instance of '\x00' (used in resynching the buffer).
    sync_re = re.compile('^.*?\x00')
    
    # regexp to determine the content length. The buffer should always start
    # with a command followed by the headers, so the content-length header will
    # always be preceded by a newline.  It may not always proceeded by a newline, though!
    content_length_re = re.compile('\ncontent-length\s*:\s*(\d+)\s*(\n|$)')
    
    def __init__(self):
        self.buffer = ''
        self.debug = False
        self.log = logging.getLogger('%s.%s' % (self.__module__, self.__class__.__name__))
    
    def clear(self):
        """
        Clears (empties) the internal buffer.
        """
        self.buffer = ''
        
    def buffer_len(self):
        """
        @return: Number of bytes in the internal buffer.
        @rtype: C{int}
        """
        return len(self.buffer)
    
    def buffer_empty(self):
        """
        @return: C{True} if buffer is empty, C{False} otherwise. 
        @rtype: C{bool}
        """
        return not bool(self.buffer)
        
    def append(self, data):
        """
        Appends bytes to the internal buffer (may or may not contain full stomp frames).
        
        @param data: The bytes to append.
        @type data: C{str}
        """
        self.buffer += data

    def extract_frame(self):
        """
        Pulls one complete frame off the buffer and returns it. 
        
        If there is no complete message in the buffer, returns None.

        Note that the buffer can contain more than once message. You
        should therefore call this method in a loop (or use iterator
        functionality exposed by class) until None returned.
        
        @return: The next complete frame in the buffer.
        @rtype: L{stomp.frame.Frame}
        """
        (mbytes, hbytes) = self._find_message_bytes(self.buffer)
        if not mbytes:
            return None
        
        msgdata = self.buffer[:mbytes]
        self.buffer = self.buffer[mbytes:]
        hdata = msgdata[:hbytes]
        # Strip off any leading whitespace from headers; this is necessary, because
        # we do not (any longer) expect a trailing \n after the \x00 byte (which means
        # it will become a leading \n to the next frame).
        hdata = hdata.lstrip() 
        elems = hdata.split('\n')
        cmd = elems.pop(0)
        headers = {}
        
        for e in elems:
            try:
                (k,v) = e.split(':', 1) # header values may contain ':' so specify maxsplit
            except ValueError:
                continue
            headers[k.strip()] = v.strip()

        # hbytes points to the start of the '\n\n' at the end of the header,
        # so 2 bytes beyond this is the start of the body. The body EXCLUDES
        # the final byte, which is  '\x00'.
        body = msgdata[hbytes + 2:-1]
        return Frame(cmd, headers=headers, body=body)


    def _find_message_bytes(self, data):
        """
        Examines passed-in data and returns a tuple of message and header lengths.
        
        Return data is a C{tuple} in the form (message_length, header_length) where 
        message_length is the length in bytes of the first complete message, if it 
        contains at least one message, or 0 if it contains no message.
        
        If message_length is non-zero, header_length contains the length in
        bytes of the header. If message_length is zero, header_length should
        be ignored.
        
        @return: A tuple in the form (message_length, header_length)
        @rtype: C{tuple}
        """

        # Sanity check. See the docstring for the method to see what it
        # does an why we need it.
        self.sync_buffer()
        
        # If the string '\n\n' does not exist, we don't even have the complete
        # header yet and we MUST exit.
        try:
            i = data.index('\n\n')
        except ValueError:
            if self.debug:
                self.log.debug("No complete frames in buffer.")
            return (0, 0)
        # If the string '\n\n' exists, then we have the entire header and can
        # check for the content-length header. If it exists, we can check
        # the length of the buffer for the number of bytes, else we check for
        # the existence of a null byte.

        # Pull out the header before we perform the regexp search. This
        # prevents us from matching (possibly malicious) strings in the
        # body.
        _hdr = self.buffer[:i]
        match = self.content_length_re.search(_hdr)
        if match:
            # There was a content-length header, so read out the value.
            content_length = int(match.groups()[0])
            
            if self.debug:
                self.log.debug("Message contains a content-length header; reading %d bytes" % content_length)
            
            # This is the content length of the body up until the null
            # byte, not the entire message. Note that this INCLUDES the 2
            # '\n\n' bytes inserted by the STOMP encoder after the body
            # (see the calculation of content_length in
            # StompEngine.callRemote()), so we only need to add 2 final bytes
            # for the footer.
            #
            #The message looks like:
            #
            #   <header>\n\n<body>\n\n\x00
            #           ^         ^^^^
            #          (i)         included in content_length!
            #
            # We have the location of the end of the header (i), so we
            # need to ensure that the message contains at least:
            #
            #     i + len ( '\n\n' ) + content_length + len ( '\x00' )
            #
            # Note that i is also the count of bytes in the header, because
            # of the fact that str.index() returns a 0-indexed value.
            req_len = i + len('\n\n') + content_length + len('\x00')
            
            if self.debug:
                self.log.debug("We have [%s] bytes and need [%s] bytes" % (len(data), req_len)) 
                
            if len(data) < req_len:
                # We don't have enough bytes in the buffer.
                if self.debug:
                    self.log.debug("Not enough bytes in buffer to construct a frame.")
                return (0, 0)
            else:
                # We have enough bytes in the buffer
                return (req_len, i)
        else:
            if self.debug:
                self.log.debug("No content-length header present; reading until first null byte.")
            # There was no content-length header, so just look for the
            # message terminator ('\x00' ).
            try:
                j = data.index('\x00')
            except ValueError:
                # We don't have enough bytes in the buffer.
                if self.debug:
                    self.log.debug("Could not find NULL termination byte.")
                return (0, 0)
            
            # j points to the 0-indexed location of the null byte. However,
            # we need to add 1 (to turn it into a byte count)
            return (j + 1, i)


    def sync_buffer(self):
        """
        Method to detect and correct corruption in the buffer.
        
        Corruption in the buffer is defined as the following conditions
        both being true:
        
            1. The buffer contains at least one newline;
            2. The text until the first newline is not a STOMP command.
        
        In this case, we heuristically try to flush bits of the buffer until
        one of the following conditions becomes true:
        
            1. the buffer starts with a STOMP command;
            2. the buffer does not contain a newline.
            3. the buffer is empty;

        If the buffer is deemed corrupt, the first step is to flush the buffer
        up to and including the first occurrence of the string '\x00', which
        is likely to be a frame boundary.

        Note that this is not guaranteed to be a frame boundary, as a binary
        payload could contain the string '\x00'. That condition would get
        handled on the next loop iteration.
        
        If the string '\x00' does not occur, the entire buffer is cleared.
        An earlier version progressively removed strings until the next newline,
        but this gets complicated because the body could contain strings that
        look like STOMP commands.
        
        Note that we do not check "partial" strings to see if they *could*
        match a command; that would be too resource-intensive. In other words,
        a buffer containing the string 'BUNK' with no newline is clearly
        corrupt, but we sit and wait until the buffer contains a newline before
        attempting to see if it's a STOMP command.
        """
        while True:
            if not self.buffer:
                # Buffer is empty; no need to do anything.
                break
            m = self.command_re.match(self.buffer)
            if m is None:
                # Buffer doesn't even contain a single newline, so we can't
                # determine whether it's corrupt or not. Assume it's OK.
                break
            cmd = m.groups()[0]
            if cmd in VALID_COMMANDS:
                # Good: the buffer starts with a command.
                break
            else:
                # Bad: the buffer starts with bunk, so strip it out. We first
                # try to strip to the first occurrence of '\x00', which
                # is likely to be a frame boundary, but if this fails, we
                # strip until the first newline.
                (self.buffer, nsubs) = self.sync_re.subn('', self.buffer)

                if nsubs:
                    # Good: we managed to strip something out, so restart the
                    # loop to see if things look better.
                    continue
                else:
                    # Bad: we failed to strip anything out, so kill the
                    # entire buffer. Since this resets the buffer to a
                    # known good state, we can break out of the loop.
                    self.buffer = ''
                    break

    def __iter__(self):
        """
        Returns an iterator object.
        """
        return self
    
    def next(self):
        """
        Return the next STOMP message in the buffer (supporting iteration).
        
        @rtype: L{stomp.frame.Frame}
        """
        msg = self.extract_frame()
        if not msg:
            raise StopIteration()
        return msg
