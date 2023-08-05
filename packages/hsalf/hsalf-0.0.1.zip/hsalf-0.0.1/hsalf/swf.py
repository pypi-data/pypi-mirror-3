# -*- coding: utf-8 -*-
'''
	hsalf.swf
	~~~~~~~~~

	Provides an object-model to Flash SWF file. The module is used to
	read and write SWF tags from or to a file-like object.

	An SWF file is opened with a SwfFile object.

	>>> fi = swf.SwfFile('example.swf')

	The file name can be omitted. In that case, you need to call either
	``load`` or ``load_header`` later.

	>>> fi = swf.SwfFile()
	>>> fi.load_header('example.swf')

	Then, you can inspect header values such as file version, frame rate.

	>>> fi.header.file_header.version
	7
	>>> fi.header.frame_header.frame_rate
	3840

	Notice that the frame rate is a 8.8 fixed point value. Therefore,
	the actual frame rate is 3840 / 256.0 = 15.0. Some tags parse the
	values to more human-understandable form, some tags do not. It is best
	to consult their docstrings.

	And you can iterate through all tags in the file with ``iter_body``.

	>>> fi.body = [tag for tag in fi.iter_body()]

	You can save this file back to disk with ``save``.

	>>> fi.save('screen2.swf')

	Like ``iter_body``, ``save`` also takes a tag generator as its second
	parameter instead of using ``body`` attribute. You can pass in the
	generator returned by ``iter_body`` to ``save``.

	>>> fi = swf.SwfFile('screen.swf')
	>>> fo = swf.SwfFile()
	>>> fo.header = fi.header
	>>> fo.save('screen2.swf', fi.iter_body())

	It is recommended to call ``close`` at the end.

	>>> fi.close()

	As a more useful example, we can write an MP3 extractor with these few
	simple lines::

		def extract_mp3(in_name, out_name):
			fo = open(out_name, 'wb')
			fi = swf.SwfFile(in_name)
			for tag in fi.iter_body():
				if tag.tag_code == swf.SOUND_STREAM_BLOCK:
					data = StringIO(tag.sound_data)
					mp3 = swf.Mp3StreamSoundData().deserialize(data)
					mp3_frames = mp3.sound_data.frames
					fo.write(mp3_frames)
			fi.close()
			fo.close()

	See more examples in ``scripts`` directory.

	:copyright: (c) 2011 Nam T. Nguyen.
	:license: MIT, see LICENSE for more details.

'''

from cStringIO import StringIO

import zlib
import struct


KEY_FRAME = 1
INTER_FRAME = 2
DISPOSABLE_INTER_FRAME = 3

SORENSON_H263_CODEC = 2
SCREEN_VIDEO_CODEC = 3

LATIN, JAPANESE, KOREAN, SIMPLIFIED_CHINESE, TRADITIONAL_CHINESE = range(1, 6)

SND_ADPCM = 1
SND_MP3 = 2

SND_MONO = 0
SND_STEREO = 1

SHOW_FRAME = 1
SET_BACKGROUND_COLOR = 9
DO_ACTION = 12
SOUND_STREAM_HEAD = 18
SOUND_STREAM_BLOCK = 19
PLACE_OBJECT_2 = 26
DEFINE_VIDEO_STREAM = 60
VIDEO_FRAME = 61


class SwfException(Exception):
	'''The top most exception class in this module.'''
	pass


class IoSwfException(SwfException):
	'''Exception related to parsing/writing SWF.'''
	pass


class CorruptedSwfException(SwfException):
	'''Exception raised when SWF file is cannot be parsed.'''
	pass


def ensure_read(f, length):
	'''Reads exactly length bytes from f.

	Returns:
		length bytes from f.
	
	Raises:
		IoSwfException: If there is less than length bytes available.
	
	'''

	s = f.read(length)
	if len(s) != length:
		raise IoSwfException('Expected {0} bytes but only available {1} '
			'bytes.'.format(length, len(s)))
	return s


class BitReader(object):
	'''BitReader reads bits from a wrapped file-like object.'''

	def __init__(self, f):
		'''Construct a BitReader object from f.

		Args:
			f (file-like object): A file-like object to be wrapped.
		
		'''

		self.fio = f
		self.backlog = ''
	
	def read(self, length, sign=False):
		'''Reads length bits from wrapped file.

		Args:
			length (int): Number of bits to read.
			sign (bool): True to treat the bits as signed value.
		
		Returns:
			An integer value.
		
		'''

		if len(self.backlog) < length:
			more = length - len(self.backlog)
			bytes = (7 + more) // 8
			bits = ['{0:08b}'.format(ord(x)) for x in \
				ensure_read(self.fio, bytes)]
			self.backlog += ''.join(bits)
		start = 1 if sign else 0
		r = int(self.backlog[start : length], 2)
		if sign and self.backlog[0] == '1':
			# take two's complement
			r = -(2 ** (length - 1) - r)
		self.backlog = self.backlog[length : ]
		return r

	def signed_read(self, length):
		'''Reads length bits from wrapped file,
		treating it as signed value.

		Args:
			length (int): Number of bits to read.
		
		Returns:
			A signed integer value.
		
		Raises:
			ValueError: If length is less than 2.

		'''

		if length < 2:
			raise ValueError('signed value must have length greater than 1')
		return self.read(length, True)

	def unsigned_read(self, length):
		'''Reads length bits from wrapped file,
		treating it as unsigned value.

		This is the same as calling `read(length, False)`.

		Args:
			length (int): Number of bits to read.
		
		Returns:
			An unsigned integer value.
		
		'''

		return self.read(length, False)
	

class BitWriter(object):
	'''BitWriter writes bits to a wrapped file-like object.'''

	def __init__(self, f):
		'''Constructs a BitWriter from f.

		Args:
			f (file-like object): A file-like object to write to.
		
		'''

		self.fio = f
		self.buffer = []
	
	def __del__(self):
		self.flush()
	
	def flush(self):
		'''Writes the buffer out to wrapped file.

		The buffer will be padded with enough 0 bits to make it byte-aligned.

		'''

		if not self.buffer:
			return
		data = b''.join(self.buffer)
		self.buffer = []
		remain = len(data) % 8
		if remain != 0:
			remain = 8 - remain
			data += b'0' * remain
		buf = []
		idx = 0
		while idx < len(data):
			c = chr(int(data[idx : idx + 8], 2))
			buf.append(c)
			idx += 8
		self.fio.write(b''.join(buf))
		self.fio.flush()
	
	@staticmethod
	def required_bits(*numbers):
		'''Returns the minimum number of bits required to represent any
		of the numbers as signed values.

		Args:
			numbers (sequence): A sequence of integer values.
		
		Returns:
			The mininum required bits.

		'''

		# min int32
		max_num = (-2) ** 31
		for num in numbers:
			# negative number?
			# take absolute value, minus 1
			# because -2 requires 1 bit to present, but 2 requires 2
			if num < 0:
				num = -num - 1
			if max_num < num:
				max_num = num
		return len('{0:b}'.format(max_num)) + 1
	
	def write(self, bits, number):
		'''Writes number to wrapped file as bits-bit value.

		Note that write does not flush. Consecutive calls to write
		will append bits to the buffer and will not byte-align it.

		Args:
			bits (int): Number of bits to represent number.
			number (int): The number to be written.
		
		'''

		if number < 0:
			number = 2 ** bits + number
		fmt = '{{0:0{0}b}}'.format(bits)
		self.buffer.append(fmt.format(number))


class SwfObject(object):
	'''An interface from which all SWF related objects are derived.

	Two methods must be provided are serialize and deserialize.

	'''

	def __init__(self):
		pass
	
	def serialize(self, f, version=0, *args, **kw_args):
		'''Writes this object to file-like object f in specified format.

		Args:
			f (file-like object): A file to write to.
		
		'''

		raise NotImplemented()
	
	def deserialize(self, f, version=0, *args, **kw_args):
		'''Populates self with data from a file-like object f.

		Args:
			f (file-like object): A file to read from.
		
		Returns:
			self: If deserialization succeeds.
			None: If not.
		
		'''

		raise NotImplemented()


class Fixed32(SwfObject):
	'''Represents a 16.16 fixed value according to SWF spec.'''

	def __init__(self, value=0):
		self.value = value

	def deserialize(self, f, version=0, *args, **kw_args):
		value = struct.unpack('<i', f.read(4))[0]
		self.value = value / 65536.0
		return self
	
	def serialize(self, f, version=0, *args, **kw_args):
		value = int(self.value * 65536.0)
		f.write(struct.pack('<i', value))


class String(SwfObject):
	'''Represents a String according to SWF spec.'''

	def __init__(self, value=''):
		pos = value.find('\x00')
		if pos >= 0:
			value = value[ : pos]
		self.value = value
	
	def deserialize(self, f, version=0, *args, **kw_args):
		r = []
		while True:
			c = ensure_read(f, 1)
			if c == '\x00':
				break
			r.append(c)
		# version 6.0 or later defaults to utf-8
		encoding = 'utf-8'
		if version < 6:
			# version 5 and below accepts ANSI (which is assumed cp1252),
			# or shift-jis, the caller should know
			encoding = kw_args.get('string_encoding', 'cp1252')
		self.value = b''.join(r).decode(encoding)
		return self
	
	def serialize(self, f, version=0, *args, **kw_args):
		encoding = 'utf-8'
		if version < 6:
			encoding = kw_args.get('string_encoding', 'cp1252')
		value = self.value.encode(encoding)
		f.write(value + '\x00')


class RgbColor(SwfObject):
	'''Represents an RGB color according to SWF spec.'''

	def __init__(self, r=0, g=0, b=0):
		self.r = r
		self.g = g
		self.b = b
	
	def deserialize(self, f, version=0, *args, **kw_args):
		self.r, self.g, self.b = struct.unpack('BBB', f.read(3))
		return self
	
	def serialize(self, f, version=0, *args, **kw_args):
		f.write(struct.pack('BBB', self.r, self.g, self.b))


class RgbaColor(SwfObject):
	'''Represents an RGBA color according to SWF spec.'''

	def __init__(self, r=0, g=0, b=0, a=0):
		self.r = r
		self.g = g
		self.b = b
		self.a = a
	
	def deserialize(self, f, version=0, *args, **kw_args):
		self.r, self.g, self.b, self.a = \
			struct.unpack('BBBB', f.read(4))
		return self
	
	def serialize(self, f, version=0, *args, **kw_args):
		f.write(struct.pack('BBBB', self.r, self.g, self.b, self.a))


class ArgbColor(SwfObject):
	'''Represents an ARGB color according to SWF spec.'''

	def __init__(self, a=0, r=0, g=0, b=0):
		self.r = r
		self.g = g
		self.b = b
		self.a = a
	
	def deserialize(self, f, version=0, *args, **kw_args):
		self.a, self.r, self.g, self.b = \
			struct.unpack('BBBB', f.read(4))
		return self
	
	def serialize(self, f, version=0, *args, **kw_args):
		f.write(struct.pack('BBBB', self.a, self.r, self.g, self.b))


class Rect(SwfObject):
	'''Represents a RECT record according to SWF spec.'''

	def __init__(self):
		self.x_min = 0
		self.x_max = 0
		self.y_min = 0
		self.y_max = 0
	
	def deserialize(self, f, version=0, *args, **kw_args):
		br = BitReader(f)
		nbits = br.unsigned_read(5)
		self.x_min = br.signed_read(nbits)
		self.x_max = br.signed_read(nbits)
		self.y_min = br.signed_read(nbits)
		self.y_max = br.signed_read(nbits)
		return self
	
	def serialize(self, f, version=0, *args, **kw_args):
		bw = BitWriter(f)
		nbits = BitWriter.required_bits(self.x_min, self.x_max,
			self.y_min, self.y_max)
		bw.write(5, nbits)
		bw.write(nbits, self.x_min)
		bw.write(nbits, self.x_max)
		bw.write(nbits, self.y_min)
		bw.write(nbits, self.y_max)
		bw.flush()
	
	def __repr__(self):
		return '%s%r' % (type(self).__name__, (
			self.x_min, self.x_max, self.y_min, self.y_max))


class Matrix(SwfObject):
	'''Represents a MATRIX record according to SWF spec.'''

	def __init__(self):
		self.scale = None
		self.rotate = None
		self.translate = [0, 0]

	def deserialize(self, f, version=0, *args, **kw_args):
		br = BitReader(f)
		has_scale = br.unsigned_read(1)
		if has_scale:
			scale_bits = br.unsigned_read(5)
			scale_x = br.signed_read(scale_bits)
			scale_y = br.signed_read(scale_bits)
			self.scale = [scale_x / 65536.0, scale_y / 65536.0]
		has_rotate = br.unsigned_read(1)
		if has_rotate:
			rotate_bits = br.unsigned_read(5)
			rotate1 = br.signed_read(rotate_bits)
			rotate2 = br.signed_read(rotate_bits)
			self.rotate = [rotate1 / 65536.0, rotate2 / 65536.0]
		translate_bits = br.unsigned_read(5)
		if translate_bits > 0:
			self.translate[0] = br.signed_read(translate_bits)
			self.translate[1] = br.signed_read(translate_bits)
		return self

	def serialize(self, f, version=0, *args, **kw_args):
		bw = BitWriter(f)
		if self.scale is not None:
			bw.write(1, 1)
			bits = BitWriter.required_bits(*self.scale)
			bw.write(5, bits)
			bw.write(bits, self.scale[0])
			bw.write(bits, self.scale[1])
		else:
			bw.write(1, 0)
		if self.rotate is not None:
			bw.write(1, 1)
			bits = BitWriter.required_bits(*self.rotate)
			bw.write(5, bits)
			bw.write(bits, self.rotate[0])
			bw.write(bits, self.rotate[1])
		else:
			bw.write(1, 0)
		if self.translate == [0, 0]:
			bw.write(5, 0)
		else:
			bits = BitWriter.required_bits(*self.translate)
			bw.write(5, bits)
			bw.write(bits, self.translate[0])
			bw.write(bits, self.translate[1])
		bw.flush()


class ColorTransform(SwfObject):
	'''Represents CXFORM structure.

	Attributes:
		mult_term (list of int): Red, green, and blue mult terms.
		add_term (list of int): Red, green, and blue add terms.

	'''

	def __init__(self):
		self.mult_term = None
		self.add_term = None
	
	def deserialize(self, f, version=0, *args, **kw_args):
		br = BitReader(f)
		has_add = br.unsigned_read(1)
		has_mult = br.unsigned_read(1)
		nbits = br.unsigned_read(4)
		if has_mult:
			self.mult_term = [br.signed_read(nbits),
				br.signed_read(nbits), br.signed_read(nbits)]
		if has_add:
			self.add_term = [br.signed_read(nbits),
				br.signed_read(nbits), br.signed_read(nbits)]
		return self
	
	def serialize(self, f, version=0, *args, **kw_args):
		bw = BitWriter(f)
		bits = [self.add_term is not None, self.mult_term is not None]
		for bit in bits:
			bw.write(1, bit)
		numbers = self.add_term if self.add_term is not None else []
		numbers.extend(self.mult_term if self.mult_term is not None else [])
		nbits = BitWriter.required_bits(*numbers)
		bw.write(4, nbits)
		if bits[1]:
			bw.write(nbits, self.mult_term[0])
			bw.write(nbits, self.mult_term[1])
			bw.write(nbits, self.mult_term[2])
		if bits[0]:
			bw.write(nbits, self.add_term[0])
			bw.write(nbits, self.add_term[1])
			bw.write(nbits, self.add_term[2])


class ColorTransformWithAlpha(SwfObject):
	'''Represents CXFORMWITHALPHA structure.

	Attributes:
		mult_term (list of int): Red, green, blue, alpha mult terms.
		add_term (list of int): Red, green, blue, alpha add terms.

	'''

	def __init__(self):
		self.mult_term = None
		self.add_term = None
	
	def deserialize(self, f, version=0, *args, **kw_args):
		br = BitReader(f)
		has_add = br.unsigned_read(1)
		has_mult = br.unsigned_read(1)
		nbits = br.unsigned_read(4)
		if has_mult:
			self.mult_term = [br.signed_read(nbits), br.signed_read(nbits),
				br.signed_read(nbits), br.signed_read(nbits)]
		if has_add:
			self.add_term = [br.signed_read(nbits), br.signed_read(nbits),
			br.signed_read(nbits), br.signed_read(nbits)]
		return self
	
	def serialize(self, f, version=0, *args, **kw_args):
		bw = BitWriter(f)
		bits = [self.add_term is not None, self.mult_term is not None]
		for bit in bits:
			bw.write(1, bit)
		numbers = self.add_term if self.add_term is not None else []
		numbers.extend(self.mult_term if self.mult_term is not None else [])
		nbits = BitWriter.required_bits(*numbers)
		bw.write(4, nbits)
		if bits[1]:
			bw.write(nbits, self.mult_term[0])
			bw.write(nbits, self.mult_term[1])
			bw.write(nbits, self.mult_term[2])
			bw.write(nbits, self.mult_term[3])
		if bits[0]:
			bw.write(nbits, self.add_term[0])
			bw.write(nbits, self.add_term[1])
			bw.write(nbits, self.add_term[2])
			bw.write(nbits, self.add_term[3])


class FileHeader(SwfObject):
	'''Represents the first 8 bytes of an SWF file.

	Attributes:
		signature (string): Either 'FWS' or 'CWS'.
		version (int): Version of this SWF file.
		file_length (int): The length of the file, including this header.

	'''

	def __init__(self):
		self.signature = 'FWS'
		self.version = 7
		self.file_length = 0
	
	def deserialize(self, f, version=0, *args, **kw_args):
		signature, version, length = \
			struct.unpack('<3sBI', f.read(8))
		if signature not in ('FWS', 'CWS'):
			raise SwfException('Invalid signature')
		self.signature = signature
		self.version = version
		self.file_length = length
		return self
	
	def _get_compressed(self):
		if self.signature[0] == 'C':
			return True
		return False
	def _set_compressed(self, b):
		if b:
			self.signature = 'CWS'
		else:
			self.signature = 'FWS'
	compressed = property(_get_compressed, _set_compressed)

	def serialize(self, f, version=0, *args, **kw_args):
		f.write(struct.pack('<3sBI', self.signature, self.version,
			self.file_length))
	

class FrameHeader(SwfObject):
	'''Represents the second part of SWFHEADER.

	Attributes:
		frame_size (Rect): Frame size, in twips.
		frame_rate (int): Number of frames per second.
		frame_count (int): Number of frames.
	
	'''

	def __init__(self):
		self.frame_size = Rect()
		self.frame_rate = 0
		self.frame_count = 0

	def deserialize(self, f, version=0, *args, **kw_args):
		size = Rect().deserialize(f)
		rate, count = struct.unpack('<HH', f.read(4))
		self.frame_size = size
		self.frame_rate = rate
		self.frame_count = count
		return self

	def serialize(self, f, version=0, *args, **kw_args):
		self.frame_size.serialize(f)
		f.write(struct.pack('<HH', self.frame_rate, self.frame_count))


class Header(SwfObject):
	'''Represents the full header record.

	Attributes:
		file_header (FileHeader): File header.
		frame_header (FrameHeader): Frame header.
	
	'''

	def __init__(self, file_header, frame_header):
		self.file_header = file_header
		self.frame_header = frame_header
	
	def deserialize(self, f, version=0, *args, **kw_args):
		raise NotImplemented()
	
	def serialize(self, f, version=0, *args, **kw_args):
		self.file_header.serialize(f)
		self.frame_header.serialize(f)


class Tag(SwfObject):
	'''Represents an SWF tag.

	Attributes:
		tag_code (int): The tag code.
		tag_length (int): The tag length, excluding tag_code and tag_length.
	
	'''
	
	def __init__(self, tag=None):
		if not tag:
			self.tag_code = 0
			self.tag_length = 0
		else:
			self.clone_tag(tag)

	def clone_tag(self, tag):
		self.tag_code = tag.tag_code
		self.tag_length = tag.tag_length
		return self
	
	def deserialize(self, f, version=0, tag=True, *args, **kw_args):
		'''Loads this tag from file-like object f.

		Args:
			f (file-like object): A file to load from.
			tag (bool): True to start from the beginning of this tag.
				False to skip tag_code and tag_length.
		
		Returns:
			self: If data were loaded successfully.
			None: Otherwise.

		'''

		if tag:
			code_and_length = struct.unpack('<H', f.read(2))[0]
			self.tag_length = code_and_length & 0b111111
			self.tag_code = code_and_length >> 6
			if self.tag_length >= 63:
				self.tag_length = struct.unpack('<I', f.read(4))[0]
		self._deserialize(f, version, *args, **kw_args)
		return self

	def _deserialize(self, f, version=0, *args, **kw_args):
		'''To be overridden by subclasses to deserialize their data.'''
		pass

	def serialize(self, f, version=0, tag=True, *args, **kw_args):
		'''Writes this tag into a file-like object.

		Args:
			f (file-like object): A file to write to.
			tag (bool): True to also write tag_code and tag_length before
				writing tag data.
		
		'''

		if not tag:
			self._serialize(f, version, *args, **kw_args)
			return
		
		data = StringIO()
		self._serialize(data, version, *args, **kw_args)
		data = data.getvalue()

		self.tag_length = len(data)
		code_and_length = self.tag_code << 6
		if self.tag_length < 63:
			code_and_length |= self.tag_length
			f.write(struct.pack('<H', code_and_length))
		else:
			code_and_length |= 63
			f.write(struct.pack('<HI', code_and_length, self.tag_length))
		f.write(data)
	
	def _serialize(self, f, version=0, *args, **kw_args):
		'''To be overridden by subclasses to serialize their data.'''
		pass


class UnknownTag(Tag):
	'''Unknown tag.'''

	def __init__(self):
		self.data = ''
	
	def _deserialize(self, f, version=0, *args, **kw_args):
		self.data = ensure_read(f, self.tag_length)

	def _serialize(self, f, version=0, *args, **kw_args):
		f.write(self.data)


class ShowFrameTag(Tag):
	'''Represents ShowFrame tag.'''

	def __init__(self):
		self.tag_code = SHOW_FRAME


class SetBackgroundColorTag(Tag):
	'''SetBackgroundColor tag.

	Attributes:
		background_color (RgbColor): The background color.
	
	'''

	def __init__(self):
		self.tag_code = SET_BACKGROUND_COLOR
		self.background_color = RgbColor()
	
	def _serialize(self, f, version=0, *args, **kw_args):
		self.background_color.serialize(f)
	
	def _deserialize(self, f, version=0, *args, **kw_args):
		self.background_color.deserialize(f)


class DoActionTag(Tag):
	'''Represents DoAction tag.

	Attributes:
		actions (sequence of ActionRecord objects): Actions to perform.
	
	'''

	def __init__(self):
		self.tag_code = DO_ACTION
		self.actions = []
	
	def _deserialize(self, f, version=0, *args, **kw_args):
		self.actions = []
		while True:
			action = ActionRecord().deserialize(f, version, *args, **kw_args)
			if action.action_code == 0:
				break
			self.actions.append(action)
	
	def _serialize(self, f, version=0, *args, **kw_args):
		for action in self.actions:
			action.serialize(f, version, *args, **kw_args)
		f.write('\x00')


class ClipEventFlags(SwfObject):
	'''Represents CLIPEVENTFLAGS structure.'''

	def __init__(self):
		self.key_up = False
		self.key_down = False
		self.mouse_up = False
		self.mouse_down = False
		self.mouse_move = False
		self.unload = False
		self.enter_frame = False
		self.load = False
		self.drag_over = False
		self.roll_out = False
		self.roll_over = False
		self.release_outside = False
		self.release = False
		self.press = False
		self.initialize = False
		self.data = False
		self.construct = False
		self.key_press = False
		self.drag_out = False
	
	def deserialize(self, f, version=0, *args, **kw_args):
		br = BitReader(f)
		self.key_up = br.unsigned_read(1)
		self.key_down = br.unsigned_read(1)
		self.mouse_up = br.unsigned_read(1)
		self.mouse_down = br.unsigned_read(1)
		self.mouse_move = br.unsigned_read(1)
		self.unload = br.unsigned_read(1)
		self.enter_frame = br.unsigned_read(1)
		self.load = br.unsigned_read(1)
		self.drag_over = br.unsigned_read(1)
		self.roll_out = br.unsigned_read(1)
		self.roll_over = br.unsigned_read(1)
		self.release_outside = br.unsigned_read(1)
		self.release = br.unsigned_read(1)
		self.press = br.unsigned_read(1)
		self.initialize = br.unsigned_read(1)
		if version < 6 and (self.drag_over or self.roll_out or \
			self.roll_over or self.release_outside or self.release or \
			self.press or self.initialize):
			raise CorruptedSwfException('Values not supported in version '
				'below 6.')
		self.data = br.unsigned_read(1)
		if version >= 6:
			t = br.unsigned_read(5)
			if t:
				raise CorruptedSwfException('Reserved must be 0')
			self.construct = br.unsigned_read(1)
			if version < 7 and self.construct:
				raise CorruptedSwfException('ClipEventConstruct must be 0 ' \
					'in version 6.')
			self.key_press = br.unsigned_read(1)
			self.drag_out = br.unsigned_read(1)
			t = br.unsigned_read(8)
			if t:
				raise CorruptedSwfException('Reserved must be 0')
		return self
	
	def serialize(self, f, version=0, *args, **kw_args):
		bw = BitWriter(f)
		bw.write(1, self.key_up)
		bw.write(1, self.key_down)
		bw.write(1, self.mouse_up)
		bw.write(1, self.mouse_down)
		bw.write(1, self.mouse_move)
		bw.write(1, self.unload)
		bw.write(1, self.enter_frame)
		bw.write(1, self.load)
		if version < 6:
			bw.write(7, 0)
		else:
			bw.write(1, self.drag_over)
			bw.write(1, self.roll_out)
			bw.write(1, self.roll_over)
			bw.write(1, self.release_outside)
			bw.write(1, self.release)
			bw.write(1, self.press)
			bw.write(1, self.initialize)
		bw.write(1, self.data)
		if version >= 6:
			bw.write(5, 0)
			if version < 7:
				bw.write(1, 0)
			else:
				bw.write(1, self.construct)
			bw.write(1, self.key_press)
			bw.write(1, self.drag_out)
			bw.write(8, 0)
		bw.flush()


class ActionRecord(SwfObject):
	'''Represents ACTIONRECORD structure.

	TODO XXX: This class needs subclassed. action_data may be removed.

	Attributes:
		action_code (int): Action code.
		action_length (int): If action code is greater or equal than 0x80,
			this field is the length of payload.
		action_data (string): The payload.
	
	'''

	def __init__(self):
		self.action_code = 0
		self.action_length = 0
		self.action_data = None

	def deserialize(self, f, version=0, *args, **kw_args):
		self.action_code = struct.unpack('B', f.read(1))[0]
		if self.action_code >= 0x80:
			self.action_length = struct.unpack('<H', f.read(1))[0]
			self.action_data = f.read(self.action_length)
		return self
	
	def serialize(self, f, version=0, *args, **kw_args):
		if self.action_code >= 0x80:
			f.write(struct.pack('<BH', self.action_code, self.action_length))
			f.write(self.action_data)
		else:
			f.write(struct.pack('B', self.action_code))


class ClipActionRecord(SwfObject):
	'''Represents CLIPACTIONRECORD structure.'''

	def __init__(self):
		self.event_flags = ClipEventFlags()
		self.record_size = 0
		self.key_code = 0
		self.actions = []
	
	def deserialize(self, f, version=0, *args, **kw_args):
		self.event_flags = ClipEventFlags().deserialize(f, version)
		self.record_size = struct.unpack('<I', f.read(4))[0]
		if self.event_flags.key_press:
			self.key_code = struct.unpack('B', f.read(1))[0]
			size = 1
		else:
			size = 0
		self.actions = []
		while size < self.record_size:
			action = ActionRecord().deserialize(f, version)
			size += 1
			if action.action_code >= 0x80:
				size += action.action_length + 2
			self.actions.append(action)
		return self
	
	def serialize(self, f, version=0, *args, **kw_args):
		self.event_flags.serialize(f, version)
		data = StringIO()
		for action in self.actions:
			action.serialize(data)
		data = data.getvalue()
		size += len(data)
		if self.event_flags.key_press:
			size += 1
			f.write(struct.pack('<IB', size, self.key_code))
		else:
			f.write(struct.pack('<I', size))
		f.write(data)


class ClipActions(SwfObject):
	'''Represents CLIPACTIONS structure.

	TODO XXX: deserialize needs f.seek().

	Attributes:
		event_flags (ClipEventFlags): Events used in these clip actions.
		records (ClipActionRecord): Individual event handlers
	
	'''

	def __init__(self):
		self.event_flags = ClipEventFlags()
		self.records = []

	def deserialize(self, f, version=0, *args, **kw_args):
		t = f.read(2)
		if t != b'\x00\x00':
			raise CorruptedSwfException('Reserved must be 0.')
		self.event_flags = ClipEventFlags().deserialize(f, version)
		self.records = []
		look_ahead_len = 4 if version >= 6 else 2
		while True:
			look_ahead = f.read(look_ahead_len)
			if look_ahead == '\x00' * look_ahead_len:
				break
			f.seek(-look_ahead_len)
			action_record = ClipActionRecord().deserialize(f, version)
			self.records.append(action_record)
		return self
	
	def serialize(self, f, version=0, *args, **kw_args):
		f.write('\x00\x00')
		self.event_flags.serialize(f, version)
		for action in self.actions:
			action.serialize(f, version)
		look_ahead_len = 4 if version >= 6 else 2
		f.write('\x00' * look_ahead_len)


class PlaceObject2Tag(Tag):
	'''PlaceObject2 tag.

	We use None for attributes' initial value to determine if they are there.

	'''

	def __init__(self):
		self.tag_code = PLACE_OBJECT_2
		self.depth = 0
		self.move = 0
		self.character_id = None
		self.matrix = None
		self.color_transform = None
		self.ratio = None
		self.name = None
		self.clip_depth = None
		self.clip_actions = None
	
	def _deserialize(self, f, version=0, *args, **kw_args):
		br = BitReader(f)
		has_clip_actions = br.unsigned_read(1)
		if version < 5 and has_clip_actions:
			raise CorruptedSwfException('HasClipActions must be 0 in ' \
				'version below 5.')
		has_clip_depth = br.unsigned_read(1)
		has_name = br.unsigned_read(1)
		has_ratio = br.unsigned_read(1)
		has_color_trans = br.unsigned_read(1)
		has_matrix = br.unsigned_read(1)
		has_char = br.unsigned_read(1)
		self.move = br.unsigned_read(1)

		self.depth = struct.unpack('<H', f.read(2))[0]
		if has_char:
			self.character_id = struct.unpack('<H', f.read(2))[0]
		if has_matrix:
			self.matrix = Matrix().deserialize(f)
		if has_color_trans:
			self.color_transform = ColorTransformWithAlpha().deserialize(f)
		if has_ratio:
			self.ratio = struct.unpack('<H', f.read(2))[0]
		if has_name:
			self.name = String().deserialize(f, version)
		if has_clip_depth:
			self.clip_depth = struct.unpack('<H', f.read(2))[0]
		if has_clip_actions and version >= 5:
			self.clip_actions = ClipActions().deserialize(f, version)

	def _serialize(self, f, version=0, *args, **kw_args):
		bits = [0] * 8
		for idx, name in enumerate(('clip_actions', 'clip_depth', 'name',
			'ratio', 'color_transform', 'matrix', 'character_id')):
			if self.__dict__.get(name, None) is not None:
				bits[idx] = 1
		bits[7] = self.move
		if version < 5:
			bits[0] = 0
		bw = BitWriter(f)
		for bit in bits:
			bw.write(1, bit)
		bw.flush()
		f.write(struct.pack('<H', self.depth))
		if self.character_id is not None:
			f.write(struct.pack('<H', self.character_id))
		if self.matrix is not None:
			self.matrix.serialize(f)
		if self.color_transform is not None:
			self.color_transform.serialize(f)
		if self.ratio is not None:
			f.write(struct.pack('<H', self.ratio))
		if self.name is not None:
			self.name.serialize(f, version)
		if self.clip_depth is not None:
			f.write(struct.pack('<H', self.clip_depth))
		if self.clip_actions is not None and version >= 5:
			self.clip_actions.serialize(f, version)


class SoundStreamHeadTag(Tag):
	'''SoundStreamHead tag.

	Attributes:
		reserved (int): Always 0.
		playback_sound_rate (int):
			0: 5.5 kHz
			1: 11 kHz
			2: 22 kHz
			3: 44 kHz
		playback_sound_size (int): Always 1 (16 bit).
		playback_sound_type (int): Either SND_MONO or SND_STEREO.
		stream_sound_compression (int): Either SND_ADPCM or SND_MP3.
			SND_MP3 is supported from SWF v4.
		stream_sound_rate (int):
			0: 5.5 kHz
			1: 11 kHz
			2: 22 kHz
			3: 44 kHz
		stream_sound_size (int): Always 1 (16 bit).
		stream_sound_type (int): Either SND_MONO or SND_STEREO.
		stream_sound_sample_count (int): Average number of samples.
		latency_seek (int): Number of samples to skip.
	
	'''

	def __init__(self):
		self.tag_code = SOUND_STREAM_HEAD
		self.reserved = 0
		self.playback_sound_rate = 0
		self.playback_sound_size = 0
		self.playback_sound_type = 0
		self.stream_sound_compression = 0
		self.stream_sound_rate = 0
		self.stream_sound_size = 0
		self.stream_sound_type = 0
		self.stream_sound_sample_count = 0
		self.latency_seek = 0
	
	def _deserialize(self, f, version=0, *args, **kw_args):
		br = BitReader(f)
		# ignore 4 bits
		br.read(4)
		self.playback_sound_rate = br.unsigned_read(2)
		self.playback_sound_size = br.unsigned_read(1)
		if self.playback_sound_size != 1:
			raise CorruptedSwfException('Playback sound size is always 1')
		self.playback_sound_type = br.unsigned_read(1)
		self.stream_sound_compression = br.unsigned_read(4)
		if self.stream_sound_compression not in (SND_ADPCM, SND_MP3):
			raise CorruptedSwfException('Stream sound compression')
		self.stream_sound_rate = br.unsigned_read(2)
		self.stream_sound_size = br.unsigned_read(1)
		if self.stream_sound_size != 1:
			raise CorruptedSwfException('Stream sound size is always 1')
		self.stream_sound_type = br.unsigned_read(1)
		self.stream_sound_sample_count = struct.unpack('<H', f.read(2))[0]
		if self.stream_sound_compression == SND_MP3 and self.tag_length > 4:
			self.latency_seek = struct.unpack('<h', f.read(2))[0]
	
	def _serialize(self, f, version=0, *args, **kw_args):
		bw = BitWriter(f)
		bw.write(4, 0)
		bw.write(2, self.playback_sound_rate)
		bw.write(1, self.playback_sound_size)
		bw.write(1, self.playback_sound_type)
		bw.write(4, self.stream_sound_compression)
		bw.write(2, self.stream_sound_rate)
		bw.write(1, self.stream_sound_size)
		bw.write(1, self.stream_sound_type)
		bw.flush()
		if self.stream_sound_compression == SND_MP3 and self.latency_seek:
			f.write(struct.pack('<Hh', self.stream_sound_sample_count,
				self.latency_seek))
		else:
			f.write(struct.pack('<H', self.stream_sound_sample_count))


class Mp3SoundData(SwfObject):
	'''Represents MP3SOUNDDATA structure.

	Attributes:
		seek_samples (int): Number of frames to be skipped.
		frames (bytestring): MP3 frames. This could be broken into MP3FRAME.
	
	'''

	def __init__(self):
		self.seek_samples = 0
		self.frames = b''
	
	def deserialize(self, f, version=0, *args, **kw_args):
		self.seek_samples = struct.unpack('<h', f.read(2))[0]
		self.frames = f.read()
		return self
	
	def serialize(self, f, version=0, *args, **kw_args):
		f.write(struct.pack('<h', self.seek_samples))
		f.write(self.frames)
	

class Mp3StreamSoundData(SwfObject):
	'''Represents MP3STREAMSOUNDDATA structure.

	Attributes:
		sample_count (int): Number of sample or sample pairs.
		sound_data (bytestring): Mp3SoundData object.

	'''

	def __init__(self):
		self.sample_count = 0
		self.sound_data = Mp3SoundData()
	
	def deserialize(self, f, version=0, *args, **kw_args):
		self.sample_count = struct.unpack('<H', f.read(2))[0]
		self.sound_data = Mp3SoundData().deserialize(f)
		return self
	
	def serialize(self, f, version=0, *args, **kw_args):
		f.write(struct.pack('<H', self.sample_count))
		self.sound_data.serialize(f)


class SoundStreamBlockTag(Tag):
	'''Represents a SoundStreamBlock.

	TODO XXX: This tag needs broken down to precise sound data block.

	Attributes:
		sound_data (bytestring): Compressed sound data.
	
	'''

	def __init__(self):
		self.tag_code = SOUND_STREAM_BLOCK
		self.sound_data = b''
	
	def _serialize(self, f, version=0, *args, **kw_args):
		f.write(self.sound_data)
	
	def _deserialize(self, f, version=0, *args, **kw_args):
		self.sound_data = f.read(self.tag_length)


class DefineVideoStreamTag(Tag):
	'''Represents a DefineVideoStream tag.'''

	def __init__(self):
		self.tag_code = DEFINE_VIDEO_STREAM
		self.character_id = 0
		self.num_frames = 0
		self.width = 0
		self.height = 0
		self.video_flags_deblocking = 0
		self.video_flags_smoothing = 0
		self.codec_id = 0
	
	def _deserialize(self, f, version=0, *args, **kw_args):
		self.character_id, self.num_frames, self.width, self.height = \
			struct.unpack('<HHHH', f.read(8))
		br = BitReader(f)
		if br.unsigned_read(4):
			raise CorruptedSwfException('Reserved value must be 0.')
		self.video_flags_deblocking = br.unsigned_read(3)
		self.video_flags_smoothing = br.unsigned_read(1)
		self.codec_id = struct.unpack('B', f.read(1))[0]
		if self.codec_id not in (2, 3, 4, 5):
			raise CorruptedSwfException('Not supported codec ID.')
		if self.codec_id >= 3 and version < 7:
			raise CorruptedSwfException('Not supported codec ID in '
				'version lower than 7.')
		if self.codec_id >= 4 and version < 8:
			raise CorruptedSwfException('Not supported codec ID in '
				'version lower than 8.')
	
	def _serialize(self, f, version=0, *args, **kw_args):
		f.write(struct.pack('<HHHH', self.character_id, self.num_frames, \
			self.width, self.height))
		bw = BitWriter(f)
		bw.write(4, 0)
		bw.write(3, self.video_flags_deblocking)
		bw.write(1, self.video_flags_smoothing)
		bw.flush()
		f.write(struct.pack('B', self.codec_id))


class ScreenVideoBlock(SwfObject):
	'''Represents a block in a Screen Video frame.

	Attributes:
		width (int): The block width.
		height (int): The block height.
		pixels (sequence of BgrColor): The pixels arranged from bottom left
			to top right.
	
	'''

	def __init__(self, width, height):
		self.width = width
		self.height = height
		self.pixels = []
	
	def __cmp__(self, other):
		if not isinstance(other, self.__class__):
			raise TypeError('Must be compared to a ScreenVideoBlock instance')
		return cmp((self.width, self.height, self.pixels),
			(other.width, other.height, other.pixels))
	
	def deserialize(self, f, version=0, *args, **kw_args):
		br = BitReader(f)
		size = br.unsigned_read(16)
		if size == 0:
			return None
		blk_data = f.read(size)
		blk_data = zlib.decompress(blk_data)
		blk_data = StringIO(blk_data)
		self.pixels = [0] * (self.width * self.height)
		pixel_nr = 0
		while pixel_nr < len(self.pixels):
			self.pixels[pixel_nr] = ScreenVideoPacket.BgrColor(). \
				deserialize(blk_data)
			pixel_nr += 1
		return self

	def serialize(self, f, version=0, *args, **kw_args):
		bw = BitWriter(f)
		if not self.pixels:
			bw.write(16, 0)
			bw.flush()
		else:
			data = StringIO()
			for pixel in self.pixels:
				pixel.serialize(data)
			data = zlib.compress(data.getvalue())
			bw.write(16, len(data))
			bw.flush()
			f.write(data)


class ScreenVideoPacket(SwfObject):
	'''Represents SCREENVIDEOPACKET according to SWF spec.

	Attributes:
		frame_type (int): Either KEY_FRAME or INTER_FRAME.
		codec_id (int): 3 for SCREEN_VIDEO_CODEC.
		block_width (int): The block width, multiple of 16.
		block_height (int): The block height, multiple of 16.
		image_width (int): The frame width.
		image_height (int): The frame height.
		hoz_blk_cnt (int): Number of blocks in a row.
		ver_blk_cnt (int): Number of blocks in a column.
		block_count (int): Number of blocks.
		image_blocks (sequence of ScreenVideoBlock): The pixel data.
	
	'''

	class BgrColor(SwfObject):
		'''Represents a BGR color.

		Attributes:
			b (int): Blue component.
			g (int): Green component.
			r (int): Red component.
		
		'''

		def __init__(self, b=0, g=0, r=0):
			self.b = b
			self.g = g
			self.r = r

		def to_rgb_tuple(self):
			return (self.r, self.g, self.b)
		
		def from_rgb_tuple(self, rgb):
			self.r, self.g, self.b = rgb
		
		def __repr__(self):
			return '%s%r' % (type(self).__name__, (
				self.b, self.g, self.r))
		
		def __cmp__(self, other):
			if isinstance(other, self.__class__):
				return cmp((self.b, self.g, self.r),
					(other.b, other.g, other.r))
			raise TypeError('Must be compared to a BgrColor instance')

		def __hash__(self):
			return hash((self.b, self.g, self.r))
		
		def deserialize(self, f, version=0, *args, **kw_args):
			self.b, self.g, self.r = struct.unpack('BBB', f.read(3))
			return self
		
		def serialize(self, f, version=0, *args, **kw_args):
			f.write(struct.pack('BBB', self.b, self.g, self.r))

	def __init__(self):
		self.frame_type = KEY_FRAME
		self.codec_id = SCREEN_VIDEO_CODEC
		self.block_width = 0
		self.block_height = 0
		self.image_width = 0
		self.image_height = 0
		self.hoz_blk_cnt = 0
		self.ver_blk_cnt = 0
		self.block_count = 0
		self.image_blocks = []
	
	def deserialize(self, f, version=0, *args, **kw_args):
		br = BitReader(f)
		self.frame_type = br.unsigned_read(4)
		codec_id = br.unsigned_read(4)
		if codec_id != SCREEN_VIDEO_CODEC:
			raise SwfException('ScreenVideoPacket is only for Screen Video codec')
		self.block_width = (br.unsigned_read(4) + 1) * 16
		self.image_width = br.unsigned_read(12)
		self.block_height = (br.unsigned_read(4) + 1) * 16
		self.image_height = br.unsigned_read(12)
		self.prepare_blocks()
		self.fill_blocks(f)
		return self
	
	def serialize(self, f, version=0, *args, **kw_args):
		bw = BitWriter(f)
		bw.write(4, self.frame_type)
		bw.write(4, self.codec_id)
		bw.write(4, self.block_width // 16 - 1)
		bw.write(12, self.image_width)
		bw.write(4, self.block_height // 16 - 1)
		bw.write(12, self.image_height)
		bw.flush()
		data = StringIO()
		for blk in self.image_blocks:
			if blk:
				blk.serialize(data)
			else:
				data.write('\x00\x00')
		f.write(data.getvalue())

	def prepare_blocks(self):
		'''Initializes this object's image_blocks.'''

		self.hoz_blk_cnt = (self.image_width + self.block_width - 1) // \
			self.block_width
		self.ver_blk_cnt = (self.image_height + self.block_height - 1) // \
			self.block_height
		self.block_count = self.hoz_blk_cnt * self.ver_blk_cnt
		self.image_blocks = [None] * self.block_count

	def get_block_dimension(self, block_nr):
		'''Returns a block's width and height.

		Args:
			block_nr (int): The block number, zero-indexed. The
				first block is at lower left corner.
		
		Returns:
			width, height (tuple): The width and height.

		'''

		row = block_nr // self.hoz_blk_cnt
		col = block_nr % self.hoz_blk_cnt
		width = self.block_width if col < self.hoz_blk_cnt - 1 else \
			self.image_width - col * self.block_width
		height = self.block_height if row < self.ver_blk_cnt - 1 else \
			self.image_height - row * self.block_height
		return width, height

	def fill_blocks(self, f):
		'''Populates this object's image_blocks with pixel data from f.
		
		Args:
			f (file-like object): A file to read from.
		
		'''

		block_nr = 0
		while block_nr < self.block_count:
			width, height = self.get_block_dimension(block_nr)
			svb = ScreenVideoBlock(width, height).deserialize(f)
			self.image_blocks[block_nr] = svb
			block_nr += 1

	def to_image(self, image):
		'''Dumps pixels to an image.

		Args:
			image (Image): An RGB image.
		
		Returns:
			image: The same passed in image.
		
		'''

		pixel_access = image.load()
		for block_nr, svb in enumerate(self.image_blocks):
			if not svb:
				continue
			row = block_nr // self.hoz_blk_cnt
			col = block_nr % self.hoz_blk_cnt
			start_y = self.image_height - (row * self.block_height) - 1
			start_x = col * self.block_width
			row = col = 0
			for pixel in svb.pixels:
				if pixel:
					y = start_y - row
					x = start_x + col
					pixel_access[x, y] = pixel.to_rgb_tuple()
				col += 1
				if col >= svb.width:
					row += 1
					col = 0
		return image
	
	def from_image(self, img, previous_frame=None,
		block_width=32, block_height=32):
		'''Fills self with data from img.

		Fills the current object with data from img. If previous_frame is
		None, this frame will be a keyframe. Otherwise, previous_frame must
		be a ScreenVideoPacket, then this frame will be an interframe. Delta
		data are calculated from img and previous_frame.

		Args:
			img (Image): A loaded RGB image.
			previous_frame (ScreenVideoPacket): The previous frame data, or
				None if this frame is a keyframe.
			block_width (int): The block width.
			block_height (int): The block height.
		
		Returns:
			None
		
		Raises:
			SwfException: If previous frame is not a ScreenVideoPacket, or
				previous_frame size is different from this frame, or
				block sizes are not multiple of 16, or
				img is not an RGB image.

		'''
		# interfame
		if previous_frame:
			if not isinstance(previous_frame, ScreenVideoPacket):
				raise SwfException('Previous frame must be a Screen Video frame')
			if (previous_frame.image_width, previous_frame.image_height) != \
				img.size:
				raise SwfException('Mismatched frame size')
			self.block_width = previous_frame.block_width
			self.block_height = previous_frame.block_height
			self.frame_type = INTER_FRAME
		# key frame
		else:
			self.block_width = block_width
			self.block_height = block_height
			self.frame_type = KEY_FRAME
		if (self.block_width % 16) != 0 or (self.block_height % 16) != 0:
			raise SwfException('Block size must be multiple of 16')
		if img.mode != 'RGB':
			raise SwfException('Source image must be in RGB mode')
		self.image_width, self.image_height = img.size
		self.prepare_blocks()
		self.fill_blocks_from_image(img, previous_frame)
	
	def fill_blocks_from_image(self, img, previous_frame=None):
		'''Grabs pixel data from an image.

		If there is a previous_frame, unchanged block will be set to None.

		Args:
			img (Image): An image to grab pixels from.
			previous_frame (ScreenVideoPacket): The previous frame.
		
		'''

		block_nr = 0
		while block_nr < self.block_count:
			width, height = self.get_block_dimension(block_nr)
			svb = ScreenVideoBlock(width, height)

			row = block_nr // self.hoz_blk_cnt
			col = block_nr % self.hoz_blk_cnt
			start_x = col * self.block_width
			stop_y = img.size[1] - row * self.block_width

			crop = img.crop((start_x, stop_y - height, start_x + width,
				stop_y))
			pixels = list(crop.getdata())

			idx = width * (height - 1)
			while idx >= 0:
				for pix in pixels[idx : idx + width]:
					pixel = ScreenVideoPacket.BgrColor()
					pixel.from_rgb_tuple(pix)
					svb.pixels.append(pixel)
				idx -= width

			# check if this block and the previous one is the same
			# if it is, we do not need this block
			if previous_frame and \
				previous_frame.image_blocks[block_nr] == svb:
				svb = None
			self.image_blocks[block_nr] = svb
			block_nr += 1

	def __repr__(self):
		return '%s%r' % (type(self).__name__, (
			self.image_width, self.image_height))


class VideoFrameTag(Tag):
	'''Represents VideoFrame tag.

	Attributes:
		stream_id (int): The stream this frame belongs to.
		frame_num (int): The frame number in that stream.
		video_data (bytestring): Frame data in encoded form.
	
	'''

	def __init__(self):
		self.tag_code = VIDEO_FRAME
		self.stream_id = 0
		self.frame_num = 0
		self.video_data = b''
	
	def _deserialize(self, f, version=0, *args, **kw_args):
		if self.tag_length < 4:
			raise CorruptedSwfException()
		self.stream_id, self.frame_num = struct.unpack('<HH', f.read(4))
		self.video_data = ensure_read(f, self.tag_length - 4)

	def _serialize(self, f, version=0, *args, **kw_args):
		# note that user must fix self.tag_length themselves before
		# calling serialize().
		f.write(struct.pack('<HH', self.stream_id, self.frame_num))
		f.write(self.video_data)


class SwfFile(SwfObject):
	'''An SWF file.

	This object is best used as an iterator. For example, to iterate
	through all tags in the SWF file::

		for tag in swf_file.iter_body():
			# do something with tag
	
	To save this object to file::

		swf_file.save('filename.swf', swf_file.iter_body())
	
	To save a compressed file, make sure the file header version is set
	to at least 6, and its compressed attribute to True::

		swf_file.header.file_header.compressed = True
		swf_file.header.file_header.version = 7
		swf_file.save(...)
	
	After an iteration completes, it cannot rewind. The list of tags
	can be saved to support multiple iterations.

	Attributes:
		header (Header): Both FileHeader and FrameHeader.
		body (list of Tag): All tags. This attribute may not present.
			See method `load`.
	
	'''

	decoders = {
		SHOW_FRAME: ShowFrameTag,
		SET_BACKGROUND_COLOR: SetBackgroundColorTag,
		DO_ACTION: DoActionTag,
		PLACE_OBJECT_2: PlaceObject2Tag,
		SOUND_STREAM_HEAD: SoundStreamHeadTag,
		SOUND_STREAM_BLOCK: SoundStreamBlockTag,
		DEFINE_VIDEO_STREAM: DefineVideoStreamTag,
		VIDEO_FRAME: VideoFrameTag,
	}

	def __init__(self, file_name=None):
		'''Constructs an SwfFile object.

		If file_name is not None, the file will be loaded. If the file
		is compressed, its content will be decompressed fully in memory,
		the original file is then closed. If the file is not compressed,
		only the header is read, the file is not closed.

		Args:
			file_name (string): A file to load from.
		
		'''

		self.header = None
		self.file = None
		if file_name:
			self.load_header(file_name)

	def close(self):
		'''Close the underlying file object.'''

		self.file.close()
	
	def __del__(self):
		if self.file:
			self.file.close()

	def load_header(self, file_name):
		'''Reads in SWF header record.

		If this SWF file is compressed, the whole file content will be
		read and decompressed into memory, the underlying file is closed.

		Args:
			file_name (string or file-like): The SWF file to be loaded.
		
		Raises:
			SwfException: If file is compressed but version is less
				than 6.
		
		'''

		# assume file_name is a file-like object
		self.file = file_name
		should_close = False
		if isinstance(file_name, str) or isinstance(file_name, unicode):
			# file_name is indeed a file_name str or unicode
			self.file = open(file_name, 'rb')
			should_close = True
		fih = FileHeader().deserialize(self.file)
		if fih.compressed:
			if fih.version < 6:
				raise SwfException('Compression is only supported '
					'from version 6')
			compressed = self.file.read()
			if should_close:
				self.file.close()
			decomp = zlib.decompress(compressed)
			self.file = StringIO(decomp)
		frh = FrameHeader().deserialize(self.file)
		self.header = Header(fih, frh)
	
	def load(self, file_name, body=True):
		'''Reads in header and, optionally, the body.

		Args:
			file_name (string or file-like): A file to read from.
			body (bool): True to populate self.body.
		
		'''

		self.load_header(file_name)
		if body:
			self.body = [tag for tag in self.iter_body()]

	def iter_body(self):
		'''Returns an iterator through all tags, including the END tag.'''

		version = self.header.file_header.version
		last_tag = None
		while True:
			try:
				tag = Tag().deserialize(self.file, version)
			except struct.error:
				if last_tag and last_tag.tag_code == 0:
					break
				raise CorruptedSwfException()
			clz = SwfFile.decoders.get(tag.tag_code, UnknownTag)
			tag = clz().clone_tag(tag).deserialize(self.file, version, False)
			yield tag
			last_tag = tag
	
	def save(self, file_name, iter_body=None):
		'''Saves self to a SWF file.

		The file_length field in SWF header will be fixed accordingly.

		Args:
			file_name (string or file-like): A file to write to. This file
				will be overwritten.
			iter_body (iterator): An iterator of Tag objects. If this
				is None, the current object's body attribute is used.
		
		Raises:
			SwfException: If iter_body is None and self.body is not set.
		
		'''

		if not iter_body:
			if 'body' not in self.__dict__:
				raise SwfException('File body is required')
			iter_body = self.body
		
		version = self.header.file_header.version
		fio = StringIO()
		self.header.frame_header.serialize(fio, version)
		for tag in iter_body:
			tag.serialize(fio, version)
		data = fio.getvalue()
		self.header.file_header.file_length = 8 + len(data)
		if self.header.file_header.compressed:
			data = zlib.compress(data)
		
		f = file_name
		should_close = False
		if isinstance(f, str) or isinstance(f, unicode):
			f = open(file_name, 'wb')
			should_close = True
		try:
			self.header.file_header.serialize(f, version)
			f.write(data)
		finally:
			if should_close:
				f.close()
