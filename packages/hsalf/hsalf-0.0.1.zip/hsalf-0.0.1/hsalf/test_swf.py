import swf
import unittest
from cStringIO import StringIO


class BitReaderTest(unittest.TestCase):

	def test_unsigned_read(self):
		#data = '0010 1000 1100 0001'
		data = StringIO(b'\x28\xC1')
		br = swf.BitReader(data)
		self.assertEqual(0, br.unsigned_read(1))
		self.assertEqual(1, br.unsigned_read(2))
		self.assertEqual(2, br.unsigned_read(3))
		self.assertEqual(3, br.unsigned_read(4))
		self.assertEqual(0, br.unsigned_read(5))
		self.assertEqual(1, br.unsigned_read(1))
		self.assertRaises(swf.IoSwfException, br.unsigned_read, 1)

	def test_signed_read(self):
		# data = '00 01 10 11'
		data = StringIO(b'\x1B')
		br = swf.BitReader(data)
		self.assertRaises(ValueError, br.signed_read, 0)
		self.assertRaises(ValueError, br.signed_read, 1)
		self.assertEqual(0, br.signed_read(2))
		self.assertEqual(1, br.signed_read(2))
		self.assertEqual(-2, br.signed_read(2))
		self.assertEqual(-1, br.signed_read(2))
		self.assertRaises(swf.IoSwfException, br.signed_read, 2)


class BitWriterTest(unittest.TestCase):

	def test_required_bits(self):
		self.assertEqual(2, swf.BitWriter.required_bits(1))
		self.assertEqual(2, swf.BitWriter.required_bits(0))
		self.assertEqual(3, swf.BitWriter.required_bits(2))
		self.assertEqual(2, swf.BitWriter.required_bits(-1))
		self.assertEqual(2, swf.BitWriter.required_bits(-2))
		self.assertEqual(3, swf.BitWriter.required_bits(-3))
		self.assertEqual(3, swf.BitWriter.required_bits(0, 1, 2, 3,
			-1, -2))
		self.assertEqual(3, swf.BitWriter.required_bits(0, 1, 2, 3,
			-1, -2, -3, -4))
		self.assertEqual(4, swf.BitWriter.required_bits(0, 1, 2, 3, 4,
			-1, -2, -3, -4, -5))

	def test_unsigned_write(self):
		f = StringIO()
		bw = swf.BitWriter(f)
		bw.write(1, 0)
		bw.write(2, 1)
		bw.write(3, 2)
		bw.write(4, 3)
		bw.write(5, 0)
		bw.write(1, 1)
		bw.flush()
		self.assertEqual(b'\x28\xC1', f.getvalue())
		f = StringIO()

	def test_signed_write(self):
		f = StringIO()
		bw = swf.BitWriter(f)
		bw.write(2, 0)
		bw.write(2, 1)
		bw.write(2, -2)
		bw.write(2, -1)
		bw.flush()
		self.assertEqual(b'\x1B', f.getvalue())
	
	def test_del(self):
		f = StringIO()
		bw = swf.BitWriter(f)
		bw.write(5, 15)
		bw.write(15, 0)
		bw.write(15, 12000)
		bw.write(15, 0)
		bw.write(15, 8000)
		del bw
		self.assertEqual(b'\x78\x00\x05\xDC\x00\x00\x0F\xA0\x00',
			f.getvalue())

		f = StringIO()
		bw = swf.BitWriter(f)
		bw.write(5, 15)
		bw.write(15, 0)
		bw.write(15, 12000)
		bw.write(15, 0)
		bw.write(15, 8000)
		bw.flush()
		del bw
		self.assertEqual(b'\x78\x00\x05\xDC\x00\x00\x0F\xA0\x00',
			f.getvalue())
	
	def test_zero_pad(self):
		f = StringIO()
		br = swf.BitWriter(f)
		br.write(7, 1)
		br.flush()
		self.assertEqual(b'\x02', f.getvalue())


class RectTest(unittest.TestCase):

	def test_serialize(self):
		rect = swf.Rect()
		rect.x_min = 0
		rect.x_max = 12000
		rect.y_min = 0
		rect.y_max = 8000
		f = StringIO()
		rect.serialize(f)
		d = f.getvalue()
		self.assertEqual(b'\x78\x00\x05\xDC\x00\x00\x0F\xA0\x00', d)


class TagTest(unittest.TestCase):

	def test_pure_serialize(self):
		tag = swf.Tag()
		tag.tag_code = 1
		tag.tag_length = 1
		f = StringIO()
		tag.serialize(f)
		self.assertEqual(b'\x40\x00', f.getvalue())

		tag.tag_length = 64
		f = StringIO()
		tag.serialize(f)
		self.assertEqual(b'\x40\x00', f.getvalue())
		
		tag.tag_code = 2
		f = StringIO()
		tag.serialize(f)
		self.assertEqual(b'\x80\x00', f.getvalue())

		tag.tag_code = 3
		f = StringIO()
		tag.serialize(f)
		self.assertEqual(b'\xC0\x00', f.getvalue())
	
	class LengthTag(swf.Tag):
		def _serialize(self, f, version=0, *args, **kw_args):
			f.write('0' * self.tag_length)
	
	def test_serialize(self):
		tag = TagTest.LengthTag()
		tag.tag_code = 1
		tag.tag_length = 1
		f = StringIO()
		tag.serialize(f)
		self.assertEqual(b'\x41\x00', f.getvalue()[ : 2])

		tag.tag_length = 63
		f = StringIO()
		tag.serialize(f)
		self.assertEqual(b'\x7F\x00\x3f\x00\x00\x00', f.getvalue()[ : 6])

		tag.tag_length = 64
		f = StringIO()
		tag.serialize(f)
		self.assertEqual(b'\x7F\x00\x40\x00\x00\x00', f.getvalue()[ : 6])

		tag.tag_code = 9
		tag.tag_length = 3
		f = StringIO()
		tag.serialize(f)
		self.assertEqual(b'\x43\x02', f.getvalue()[ : 2])
	

if __name__ == '__main__':
	unittest.main()
