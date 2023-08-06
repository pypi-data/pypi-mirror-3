// Copyright (C) 2011-2012 CRS4.
//
// This file is part of Seal.
//
// Seal is free software: you can redistribute it and/or modify it
// under the terms of the GNU General Public License as published by the Free
// Software Foundation, either version 3 of the License, or (at your option)
// any later version.
//
// Seal is distributed in the hope that it will be useful, but
// WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
// or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
// for more details.
//
// You should have received a copy of the GNU General Public License along
// with Seal.  If not, see <http://www.gnu.org/licenses/>.


package tests.it.crs4.seal.common;

import it.crs4.seal.common.FastqInputFormat.FastqRecordReader;
import it.crs4.seal.common.SequencedFragment;

import java.io.File;
import java.io.IOException;
import java.io.PrintWriter;
import java.io.BufferedWriter;
import java.io.FileWriter;

import org.junit.*;
import static org.junit.Assert.*;

import org.apache.hadoop.mapred.JobConf;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.FSDataInputStream;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.lib.input.FileSplit;

public class TestFastqInputFormat
{
	public static final String oneFastq =
		"@ERR020229.10880 HWI-ST168_161:1:1:1373:2042/1\n" +
		"TTGGATGATAGGGATTATTTGACTCGAATATTGGAAATAGCTGTTTATATTTTTTAAAAATGGTCTGTAACTGGTGACAGGACGCTTCGAT\n" +
		"+\n" +
		"###########################################################################################";

	public static final String twoFastq =
		"@ERR020229.10880 HWI-ST168_161:1:1:1373:2042/1\n" +
		"TTGGATGATAGGGATTATTTGACTCGAATATTGGAAATAGCTGTTTATATTTTTTAAAAATGGTCTGTAACTGGTGACAGGACGCTTCGAT\n" +
		"+\n" +
		"###########################################################################################\n" +

		"@ERR020229.10883 HWI-ST168_161:1:1:1796:2044/1\n" +
		"TGAGCAGATGTGCTAAAGCTGCTTCTCCCCTAGGATCATTTGTACCTACCAGACTCAGGGAAAGGGGTGAGAATTGGGCCGTGGGGCAAGG\n" +
		"+\n" +
		"BDDCDBDD?A=?=:=7,7*@A;;53/53.:@>@@4=>@@@=?1?###############################################";

	public static final String illuminaFastq =
		"@EAS139:136:FC706VJ:2:5:1000:12850 1:Y:18:ATCACG\n" +
		"TTGGATGATAGGGATTATTTGACTCGAATATTGGAAATAGCTGTTTATATTTTTTAAAAATGGTCTGTAACTGGTGACAGGACGCTTCGAT\n" +
		"+\n" +
		"###########################################################################################";

	public static final String illuminaFastqWithPhred64Quality =
		"@EAS139:136:FC706VJ:2:5:1000:12850 1:Y:18:ATCACG\n" +
		"TTGGATGATAGGGATTATTTGACTCGAATATTGGAAATAGCTGTTTATATTTTTTAAAAATGGTCTGTAACTGGTGACAGGACGCTTCGAT\n" +
		"+\n" +
		"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb";

	public static final String oneFastqWithoutRead =
		"@ERR020229.10880 HWI-ST168_161:1:1:1373:2042\n" +
		"TTGGATGATAGGGATTATTTGACTCGAATATTGGAAATAGCTGTTTATATTTTTTAAAAATGGTCTGTAACTGGTGACAGGACGCTTCGAT\n" +
		"+\n" +
		"###########################################################################################";

	public static final String fastqWithIdTwice =
		"@ERR020229.10880 HWI-ST168_161:1:1:1373:2042/1\n" +
		"TTGGATGATAGGGATTATTTGACTCGAATATTGGAAATAGCTGTTTATATTTTTTAAAAATGGTCTGTAACTGGTGACAGGACGCTTCGAT\n" +
		"+ERR020229.10880 HWI-ST168_161:1:1:1373:2042/1\n" +
		"###########################################################################################";

	public static final String fastqWithAmpersandQuality =
		"+lousy.id HWI-ST168_161:1:1:1373:2042/1\n" +
		"@##########################################################################################\n" +
		"@ERR020229.10880 HWI-ST168_161:1:1:1373:2042/1\n" +
		"TTGGATGATAGGGATTATTTGACTCGAATATTGGAAATAGCTGTTTATATTTTTTAAAAATGGTCTGTAACTGGTGACAGGACGCTTCGAT\n" +
		"+ERR020229.10880 HWI-ST168_161:1:1:1373:2042/1\n" +
		"###########################################################################################";


	private JobConf conf;
	private FileSplit split;
	private File tempFastq;

	private Text key;
	private SequencedFragment fragment;

	@Before
	public void setup() throws IOException
	{
		tempFastq = File.createTempFile("test_fastq_input_format", "fastq");
		conf = new JobConf();
		key = new Text();
		fragment = new SequencedFragment();
	}

	@After
	public void teardDown()
	{
		tempFastq.delete();
		split = null;
	}

	private void writeToTempFastq(String s) throws IOException
	{
		PrintWriter fastqOut = new PrintWriter( new BufferedWriter( new FileWriter(tempFastq) ) );
		fastqOut.write(s);
		fastqOut.close();
	}

	private FastqRecordReader createReaderForOneFastq() throws IOException
	{
		writeToTempFastq(oneFastq);
		split = new FileSplit(new Path(tempFastq.toURI().toString()), 0, oneFastq.length(), null);

		return new FastqRecordReader(conf, split);
	}

	@Test
	public void testReadFromStart() throws IOException
	{
		FastqRecordReader reader = createReaderForOneFastq();

		assertEquals(0, reader.getPos());
		assertEquals(0.0, reader.getProgress(), 0.01);

		boolean retval = reader.next(key, fragment);
		assertTrue(retval);
		assertEquals("ERR020229.10880 HWI-ST168_161:1:1:1373:2042/1", key.toString());
		assertEquals("TTGGATGATAGGGATTATTTGACTCGAATATTGGAAATAGCTGTTTATATTTTTTAAAAATGGTCTGTAACTGGTGACAGGACGCTTCGAT", fragment.getSequence().toString());
		assertEquals("###########################################################################################", fragment.getQuality().toString());

		assertEquals(oneFastq.length(), reader.getPos());
		assertEquals(1.0, reader.getProgress(), 0.01);

		retval = reader.next(key, fragment);
		assertFalse(retval);
	}

	@Test
	public void testReadStartInMiddle() throws IOException
	{
		writeToTempFastq(twoFastq);
		split = new FileSplit(new Path(tempFastq.toURI().toString()), 10, twoFastq.length() - 10, null);

		FastqRecordReader reader = new FastqRecordReader(conf, split);

		assertEquals(oneFastq.length() + 1, reader.getPos()); // The start of the second record. We +1 for the \n that is not in oneFastq
		assertEquals(0.0, reader.getProgress(), 0.01);

		boolean retval = reader.next(key, fragment);
		assertTrue(retval);
		assertEquals("ERR020229.10883 HWI-ST168_161:1:1:1796:2044/1", key.toString());
		assertEquals("TGAGCAGATGTGCTAAAGCTGCTTCTCCCCTAGGATCATTTGTACCTACCAGACTCAGGGAAAGGGGTGAGAATTGGGCCGTGGGGCAAGG", fragment.getSequence().toString());
		assertEquals("BDDCDBDD?A=?=:=7,7*@A;;53/53.:@>@@4=>@@@=?1?###############################################", fragment.getQuality().toString());

		assertEquals(twoFastq.length(), reader.getPos()); // now should be at the end of the data
		assertEquals(1.0, reader.getProgress(), 0.01);

		retval = reader.next(key, fragment);
		assertFalse(retval);
	}

	@Test
	public void testSliceEndsBeforeEndOfFile() throws IOException
	{
		writeToTempFastq(twoFastq);
		// slice ends at position 10--i.e. somewhere in the first record.  The second record should not be read.
		split = new FileSplit(new Path(tempFastq.toURI().toString()), 0, 10, null);

		FastqRecordReader reader = new FastqRecordReader(conf, split);

		boolean retval = reader.next(key, fragment);
		assertTrue(retval);
		assertEquals("ERR020229.10880 HWI-ST168_161:1:1:1373:2042/1", key.toString());

		assertFalse("FastqRecordReader is reading a record that starts after the end of the slice", reader.next(key, fragment));
	}

	@Test
	public void testGetReadNumFromName() throws IOException
	{
		FastqRecordReader reader = createReaderForOneFastq();
		boolean retval = reader.next(key, fragment);
		assertTrue(retval);
		assertEquals(1, fragment.getRead().intValue());
	}

	@Test
	public void testNameWithoutReadNum() throws IOException
	{
		writeToTempFastq(oneFastqWithoutRead);
		split = new FileSplit(new Path(tempFastq.toURI().toString()), 0, oneFastqWithoutRead.length(), null);

		FastqRecordReader reader = new FastqRecordReader(conf, split);
		boolean retval = reader.next(key, fragment);
		assertTrue(retval);
		assertNull("Read is not null", fragment.getRead());
	}

	@Test
	public void testIlluminaMetaInfo() throws IOException
	{
		writeToTempFastq(illuminaFastq);
		split = new FileSplit(new Path(tempFastq.toURI().toString()), 0, illuminaFastq.length(), null);

		FastqRecordReader reader = new FastqRecordReader(conf, split);
		boolean found = reader.next(key, fragment);
		assertTrue(found);

		assertEquals("EAS139", fragment.getInstrument());
		assertEquals(136, fragment.getRunNumber().intValue());
		assertEquals("FC706VJ", fragment.getFlowcellId());
		assertEquals(2, fragment.getLane().intValue());
		assertEquals(5, fragment.getTile().intValue());
		assertEquals(1000, fragment.getXpos().intValue());
		assertEquals(12850, fragment.getYpos().intValue());
		assertEquals(1, fragment.getRead().intValue());
		assertEquals(false, fragment.getFilterPassed().booleanValue());
		assertEquals(18, fragment.getControlNumber().intValue());
		assertEquals("ATCACG", fragment.getIndexSequence());
	}

	@Test
	public void testOneIlluminaThenNot() throws IOException
	{
		writeToTempFastq(illuminaFastq + "\n" + oneFastq);
		split = new FileSplit(new Path(tempFastq.toURI().toString()), 0, illuminaFastq.length() + oneFastq.length() + 1, null);

		FastqRecordReader reader = new FastqRecordReader(conf, split);

		assertTrue(reader.next(key, fragment));
		assertEquals("EAS139", fragment.getInstrument());

		assertTrue(reader.next(key, fragment));
		assertNull(fragment.getInstrument());

		assertFalse(reader.next(key, fragment));
	}

	@Test
	public void testOneNotThenIllumina() throws IOException
	{
		writeToTempFastq(oneFastq + "\n" + illuminaFastq);
		split = new FileSplit(new Path(tempFastq.toURI().toString()), 0, illuminaFastq.length() + oneFastq.length() + 1, null);

		FastqRecordReader reader = new FastqRecordReader(conf, split);

		assertTrue(reader.next(key, fragment));
		assertNull(fragment.getInstrument());

		assertTrue(reader.next(key, fragment));
		assertNull(fragment.getInstrument());

		assertFalse(reader.next(key, fragment));
	}

	@Test
	public void testProgress() throws IOException
	{
		writeToTempFastq(twoFastq);
		split = new FileSplit(new Path(tempFastq.toURI().toString()), 0, twoFastq.length(), null);

		FastqRecordReader reader = new FastqRecordReader(conf, split);
		assertEquals(0.0, reader.getProgress(), 0.01);

		reader.next(key, fragment);
		assertEquals(0.5, reader.getProgress(), 0.01);

		reader.next(key, fragment);
		assertEquals(1.0, reader.getProgress(), 0.01);
	}

	@Test
	public void testCreateKey() throws IOException
	{
		FastqRecordReader reader = createReaderForOneFastq();
		assertTrue(reader.createKey() instanceof Text);
	}

	@Test
	public void testCreateValue() throws IOException
	{
		FastqRecordReader reader = createReaderForOneFastq();
		assertTrue(reader.createValue() instanceof SequencedFragment);
	}

	@Test
	public void testClose() throws IOException
	{
		FastqRecordReader reader = createReaderForOneFastq();
		// doesn't really do anything but exercise the code
		reader.close();
	}

	@Test
	public void testReadFastqWithIdTwice() throws IOException
	{
		writeToTempFastq(fastqWithIdTwice);
		split = new FileSplit(new Path(tempFastq.toURI().toString()), 0, fastqWithIdTwice.length(), null);

		FastqRecordReader reader = new FastqRecordReader(conf, split);

		boolean retval = reader.next(key, fragment);
		assertTrue(retval);
		assertEquals("ERR020229.10880 HWI-ST168_161:1:1:1373:2042/1", key.toString());
		assertEquals("TTGGATGATAGGGATTATTTGACTCGAATATTGGAAATAGCTGTTTATATTTTTTAAAAATGGTCTGTAACTGGTGACAGGACGCTTCGAT", fragment.getSequence().toString());
		assertEquals("###########################################################################################", fragment.getQuality().toString());

		retval = reader.next(key, fragment);
		assertFalse(retval);
	}

	@Test
	public void testReadFastqWithAmpersandQuality() throws IOException
	{
		writeToTempFastq(fastqWithAmpersandQuality);
		// split doesn't start at 0, forcing reader to advance looking for first complete record
		split = new FileSplit(new Path(tempFastq.toURI().toString()), 3, fastqWithAmpersandQuality.length(), null);

		FastqRecordReader reader = new FastqRecordReader(conf, split);

		boolean retval = reader.next(key, fragment);
		assertTrue(retval);
		assertEquals("ERR020229.10880 HWI-ST168_161:1:1:1373:2042/1", key.toString());
		assertEquals("TTGGATGATAGGGATTATTTGACTCGAATATTGGAAATAGCTGTTTATATTTTTTAAAAATGGTCTGTAACTGGTGACAGGACGCTTCGAT", fragment.getSequence().toString());
		assertEquals("###########################################################################################", fragment.getQuality().toString());

		retval = reader.next(key, fragment);
		assertFalse(retval);
	}

	@Test
	public void testMakePositionMessage() throws IOException
	{
		writeToTempFastq(fastqWithIdTwice);
		split = new FileSplit(new Path(tempFastq.toURI().toString()), 0, fastqWithIdTwice.length(), null);

		FastqRecordReader reader = new FastqRecordReader(conf, split);
		assertNotNull(reader.makePositionMessage());
	}

	@Test
	public void testFastqWithPhred64() throws IOException
	{
		writeToTempFastq(illuminaFastqWithPhred64Quality);
		split = new FileSplit(new Path(tempFastq.toURI().toString()), 0, illuminaFastqWithPhred64Quality.length(), null);

		conf.set("seal.fastq-input.base-quality-encoding", "illumina");
		FastqRecordReader reader = new FastqRecordReader(conf, split);
		boolean found = reader.next(key, fragment);
		assertTrue(found);
		assertEquals("CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC", fragment.getQuality().toString());
	}
}
