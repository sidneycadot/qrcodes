#! /usr/bin/env -S python3 -B

def test():

	s = '点茗'

	for c in s:
		value = int.from_bytes(c.encode('shift-jis'), byteorder='big')
		if (0x8140 <= value <= 0x9ffc):
			value -= 0x8140
		elif (0xe040 <= value <= 0xebbf):
			value -= 0xc140
		else:
			raise ValueError()

		msb = value // 256
		lsb = value % 256
		value = msb * 0xc0 + lsb

		print(c, hex(value))

for k in range(0x10000):
	ok = (0x8140 <= k <= 0x9ffc) or (0xe040 <= k <= 0xebbf)
	if not ok:
		continue
	b = int.to_bytes(k, length=2, byteorder='big')
	try:
		character = b.decode('shift-jis')
	except UnicodeDecodeError:
		continue
	print(k, character)
