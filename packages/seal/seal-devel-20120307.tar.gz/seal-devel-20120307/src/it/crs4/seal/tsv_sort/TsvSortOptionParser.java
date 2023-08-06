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

package it.crs4.seal.tsv_sort;

import it.crs4.seal.common.ClusterUtils;
import it.crs4.seal.common.SealToolParser;

import java.util.ArrayList;
import java.io.IOException;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;

import org.apache.commons.cli.*;

public class TsvSortOptionParser {

	public static final int DEFAULT_RED_TASKS_PER_NODE = 3;
	public static final String ConfigSection = "TsvSort";

	private SealToolParser parser;
	private Options sortOptions;
	private Option keyOption;
	private Option delimiterOption;

	public TsvSortOptionParser()
	{
		// define the options
		sortOptions = new Options();

		keyOption = OptionBuilder
		              .withDescription("sort key list. Comma-separated numbers, ranges specified with '-' [default: whole line]")
		              .hasArg()
		              .withArgName("index[-last_index]")
		              .withLongOpt("key")
		              .create("k");
		sortOptions.addOption(keyOption);

		delimiterOption = OptionBuilder
		              .withDescription("character string that delimits fields [default: <TAB>]")
		              .hasArg()
		              .withArgName("DELIM")
		              .withLongOpt("field-separator")
		              .create("t");
		sortOptions.addOption(delimiterOption);

		parser = new SealToolParser(ConfigSection, sortOptions);
		parser.setMinReduceTasks(1);
	}

	public void parse(Configuration conf, String[] args) throws IOException
	{
		try
		{
			CommandLine line = parser.parseOptions(conf, args);

			if (line.hasOption(keyOption.getOpt()))
				conf.set(TsvInputFormat.COLUMN_KEYS_CONF, line.getOptionValue(keyOption.getOpt()));

			if (line.hasOption(delimiterOption.getOpt()))
			{
				String delim = line.getOptionValue(delimiterOption.getOpt());
				conf.set(TsvInputFormat.DELIM_CONF, delim);
			}
		}
		catch( ParseException e )
		{
			parser.defaultUsageError("it.crs4.seal.tsv_sort.TsvSort", e.getMessage()); // doesn't return
		}

		// set number of reduce tasks to use
		conf.set(ClusterUtils.NUM_RED_TASKS_PROPERTY, String.valueOf(getNReduceTasks()));
	}

	public ArrayList<Path> getInputPaths()
	{
		ArrayList<Path> retval = new ArrayList<Path>(parser.getNumInputPaths());
		for (Path p: parser.getInputPaths())
			retval.add(p);

		return retval;
	}

	public Path getOutputPath() { return parser.getOutputPath(); }

	public int getNReduceTasks()
 	{
		try {
			return parser.getNReduceTasks(DEFAULT_RED_TASKS_PER_NODE);
		} catch (IOException e) {
			throw new RuntimeException(e);
		}
 	}
}
