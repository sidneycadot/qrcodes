#! /usr/bin/env -S python3 -B

from qrcode_generator.kanji_encode import kanji_character_value


def show_example_characters():

	examples = {
		'点' : 0x0d9f,  # Section 7.4.6, 0x935f
		'茗' : 0x1aaa,  # Section 7.4.6, 0xe4aa
		'日' : 0x0e3a,  # Section 8.3, 0x93fa
		'本' : 0x0ffb   # Section 8.3, 0x967b
	}

	for (c, reference_value) in examples.items():
		value = kanji_character_value(c)
		print(f"{c} 0x{value:04x}")
		assert value == reference_value


def enumerate_all_representable_kanji_characters():
	representable_kanji_characters = []
	for k in range(0x10000):
		ok = (0x8140 <= k <= 0x9ffc) or (0xe040 <= k <= 0xebbf)
		if not ok:
			continue
		b = int.to_bytes(k, length=2, byteorder='big')
		try:
			character = b.decode('shift-jis')
		except UnicodeDecodeError:
			continue
		else:
			representable_kanji_characters.append(character)

	print(f"Number of representable Kanji characters: {len(representable_kanji_characters)}.")


def main():
	enumerate_all_representable_kanji_characters()
	show_example_characters()


if __name__ == "__main__":
	main()
