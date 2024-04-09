def test_basic_3():
  expected = [
    0b000,
    0b001,
    0b000,
    0b010,
    0b000,
    0b100,
  ]

  assert expected == generate(mode=0, inverted=0, pins=3)

def test_inverted_3():
  expected = [
    0b111,
    0b110,
    0b111,
    0b101,
    0b111,
    0b011,
  ]

  assert expected == generate(mode=0, inverted=1, pins=3)

def test_overlap_3():
  expected = [
    0b101,
    0b001,
    0b011,
    0b010,
    0b110,
    0b100,
  ]

  assert expected == generate(mode=1, inverted=0, pins=3)

def test_overlap_inverted_3():
  expected = [
    0b010,
    0b110,
    0b100,
    0b101,
    0b001,
    0b011,
  ]

  assert expected == generate(mode=1, inverted=1, pins=3)

def test_overlap_inverted_5():
  expected = [
    0b01110,
    0b11110,
    0b11100,
    0b11101,
    0b11001,
    0b11011,
    0b10011,
    0b10111,
    0b00111,
    0b01111,
  ]

  assert expected == generate(mode=1, inverted=1, pins=5)

def test_overlap_5():
  expected = [
    0b10001,
    0b00001,
    0b00011,
    0b00010,
    0b00110,
    0b00100,
    0b01100,
    0b01000,
    0b11000,
    0b10000,
  ]

  assert expected == generate(mode=1, inverted=0, pins=5)

def test_5():
  expected = [
    0b00000,
    0b00001,
    0b00000,
    0b00010,
    0b00000,
    0b00100,
    0b00000,
    0b01000,
    0b00000,
    0b10000,
  ]

  assert expected == generate(mode=0, inverted=0, pins=5)

def test_2():
  expected = [
    0b00,
    0b01,
    0b00,
    0b10,
  ]

  assert expected == generate(mode=0, inverted=0, pins=2)

def test_2_inverted():
  expected = [
    0b11,
    0b10,
    0b11,
    0b01,
  ]

  assert expected == generate(mode=0, inverted=1, pins=2)

def test_2_overlap():
  expected = [
    0b11,
    0b01,
    0b11,
    0b10,
  ]

  assert expected == generate(mode=1, inverted=0, pins=2)

def test_4_overlap():
  expected = [
    0b1001,
    0b0001,
    0b0011,
    0b0010,
    0b0110,
    0b0100,
    0b1100,
    0b1000,
  ]

  assert expected == generate(mode=1, inverted=0, pins=4)

def test_4_overlap_inverted():
  expected = [i^0b1111 for i in [
    0b1001,
    0b0001,
    0b0011,
    0b0010,
    0b0110,
    0b0100,
    0b1100,
    0b1000,
  ]]

  assert expected == generate(mode=1, inverted=1, pins=4)

def generate(mode=0, inverted=0, pins=3):
  out_pins = []
  mask = ((1 << pins) - 1) * inverted
  for i in range(0, pins):
    a = mode * (pow(2, (i - 1) % pins) + pow(2, i))
    out_pins.append(a^mask)
    b = pow(2, i)
    out_pins.append(b^mask)

  return out_pins
