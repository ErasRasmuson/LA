/*
 * Copyright 2015 data Artisans GmbH
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *  http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package pack.datatypes;

import org.joda.time.DateTime;
import org.joda.time.format.DateTimeFormat;
import org.joda.time.format.DateTimeFormatter;

import java.util.Locale;

public class TestData implements Comparable<TestData> {

	private static transient DateTimeFormatter timeFormatter =
			//DateTimeFormat.forPattern("yyyy-MM-dd HH:mm:ss").withLocale(Locale.US).withZoneUTC();
			DateTimeFormat.forPattern("yyyy-MM-dd HH:mm:ss").withZoneUTC();
			//DateTimeFormat.forPattern("yyyy-MM-dd HH:mm:ss");

	public TestData() {}

	public TestData(DateTime eventTime,
					int eventId,
					String eventIdStr,
					String sources,
					String targets,
					String attr,
					String data,
					String evId1,
					String targetEvId,
					boolean testFlag)
	{
		this.eventTime = eventTime;
		this.eventId = 0;
		this.eventIdStr = eventIdStr;
		this.sources = sources;
		this.targets = targets;
		this.attr = attr;
		this.data = data;
		this.data = evId1;
		this.data = targetEvId;
		this.testFlag = testFlag;
	}

	public DateTime eventTime;
	public int eventId;
	public String eventIdStr;
	public String sources;
	public String targets;
	public String attr;
	public String data;
	public String evId1="";
	public String targetEvId="";
	public boolean testFlag = true;

	public String toString() {
		StringBuilder sb = new StringBuilder();
		//sb.append(eventTime.toString(timeFormatter)).append(",");
		sb.append(eventTime).append(",");
		sb.append(eventId).append(",");
		sb.append(eventIdStr).append(",");
		sb.append(sources).append(",");
		sb.append(targets).append(",");
		sb.append(attr).append(",");
		sb.append(data).append(",");

		return sb.toString();
	}

	public static TestData fromString(String line) {

		String[] tokens = line.split(",");
		int tokensLen = tokens.length;
		if (tokensLen != 6) {
			throw new RuntimeException("Invalid record: " + line + " tokens: " + tokensLen);
		}

		// Gets parts of Id
		String[] tokensId = tokens[1].split("\\.");
		if (tokensId.length != 2) {
			throw new RuntimeException("Invalid Id record: " + tokens[1]);
		}

		TestData data = new TestData();

		try {

			// Generates numerical event Id
			int eventId1  = tokensId[0].length() > 0 ? Integer.parseInt(tokensId[0]): 0;
			int eventId2  = tokensId[1].length() > 0 ? Integer.parseInt(tokensId[1]): 0;
			data.eventId  = eventId1 * 1000 + eventId2;
			System.out.print(" - eventId: " + data.eventId  + "\n");
			System.out.flush();

			data.eventTime = DateTime.parse(tokens[0], timeFormatter);
			//data.eventTime = tokens[0].length() > 0 ? Long.parseLong(tokens[0]) : 0;
			//data.eventId  = tokens[1].length() > 0 ? Float.parseFloat(tokens[1]) : 0;
			data.eventIdStr  = tokens[1].length() > 0 ? tokens[1]: "-";
			data.sources  = tokens[2].length() > 0 ? tokens[2] : "-";;
			data.targets  = tokens[3].length() > 0 ? tokens[3] : "-";;
			data.attr  = tokens[4].length() > 0 ? tokens[4] : "-";;
			data.data  = tokens[5].length() > 0 ? tokens[5] : "-";;

		} catch (NumberFormatException nfe) {
			throw new RuntimeException("Invalid record B: " + line, nfe);
		}

		return data;
	}

	public int compareTo(TestData other) {
		if (other == null) {
			return 1;
		}
		int compareTimes = Long.compare(this.getEventTime(), other.getEventTime());

		return compareTimes;
	}

	@Override
	public boolean equals(Object other) {
		return other instanceof TestData &&
				this.eventId == ((TestData) other).eventId;
	}

	@Override
	public int hashCode() {
		//return (int)this.eventId;
        return this.eventId;
	}

	public long getEventTime() {
		return eventTime.getMillis();
		//return eventTime;
	}
	public int getEventId() {
		return eventId;
	}
}
