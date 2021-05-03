# Functions that implment yencoding of data to replace escape characters with 2 bytes.
# Used to filter binary data to facilitae transport over a serial connection

GEN_OFFSET = 42 
ESC_OFFSET = 64

iLF = 10
iCR = 13
iESC = ord("=")
iNUL = 0
iZERO = ord("0")

def b(int_val): 
	return bytes([int_val % 256])

def yencode(in_buf):
	out_buf = b''
	buf_len = len(in_buf)
	for col in range(buf_len):
		byte = in_buf[col:col+1]
		ibyte = (int.from_bytes(byte, byteorder='big') + GEN_OFFSET) % 256
		if (ibyte == iLF) or (ibyte == iCR) or (ibyte == iESC) or (ibyte == iNUL) or (ibyte == iZERO):
			out_buf += b(int_ESC) + ((ibyte + ESC_OFFSET) % 256).to_bytes(1, byteorder='big')
		else:
			out_buf += b(ibyte)
	return out_buf

def ydecode(in_buf):
	out_buf = b''; ESC_happened = False
	buf_len = len(in_buf)
	for col in range(buf_len):
		byte = in_buf[col:col+1]
		ibyte = int.from_bytes(byte, byteorder='big')
		if ESC_happened:
			replacement_byte = ((ibyte - GEN_OFFSET - ESC_OFFSET) % 256).to_bytes(1, byteorder='big')
			out_buf += replacement_byte
			ESC_happened = False
		elif ibyte == iESC:
			ESC_happened = True
		else:
			out_buf += ((ibyte - GEN_OFFSET) % 256).to_bytes(1, byteorder='big')
	return out_buf
