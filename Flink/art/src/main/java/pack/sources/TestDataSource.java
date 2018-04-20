
package pack.sources;

import pack.datatypes.TestData;
import org.apache.flink.streaming.api.checkpoint.ListCheckpointed;
import org.apache.flink.streaming.api.functions.source.SourceFunction;
import org.apache.flink.streaming.api.watermark.Watermark;
import java.io.BufferedReader;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.util.Collections;
import java.util.List;
import java.util.zip.GZIPInputStream;

public class TestDataSource implements SourceFunction<TestData>, ListCheckpointed<Long> {

	private final String dataFilePath;
	private final int servingSpeed;

	private transient BufferedReader reader;
	private transient InputStream gzipStream;

	// state
	// number of emitted events
	private long eventCnt = 0;

	/**
	 * Serves the TaxiRide records from the specified and ordered gzipped input file.
	 * Rides are served out-of time stamp order with specified maximum random delay
	 * in a serving speed which is proportional to the specified serving speed factor.
	 *
	 * @param dataFilePath The gzipped input file from which the TaxiRide records are read.
	 */
	public TestDataSource(String dataFilePath) {
		this(dataFilePath, 1);
	}

	/**
	 * Serves the TaxiRide records from the specified and ordered gzipped input file.
	 * Rides are served exactly in order of their time stamps
	 * in a serving speed which is proportional to the specified serving speed factor.
	 *
	 * @param dataFilePath The gzipped input file from which the TaxiRide records are read.
	 * @param servingSpeedFactor The serving speed factor by which the logical serving time is adjusted.
	 */
	public TestDataSource(String dataFilePath, int servingSpeedFactor) {
		this.dataFilePath = dataFilePath;
		this.servingSpeed = servingSpeedFactor;
	}

	@Override
	public void run(SourceContext<TestData> sourceContext) throws Exception {

		final Object lock = sourceContext.getCheckpointLock();

		gzipStream = new GZIPInputStream(new FileInputStream(dataFilePath));
		reader = new BufferedReader(new InputStreamReader(gzipStream, "UTF-8"));

		Long prevEventTime = null;

		String line;
		long cnt = 0;

		// skip emitted events
		/*while (cnt < eventCnt && reader.ready() && (line = reader.readLine()) != null) {
			cnt++;
			TestData event = TestData.fromString(line);
			prevEventTime = getEventTime(event);
		}*/

		System.out.print(" Java reader .. \n");
		System.out.flush();

		// emit all subsequent events proportial to their timestamp
		while (reader.ready() && (line = reader.readLine()) != null) {
			cnt++;
			if (cnt > 1) {
				System.out.print(" - line: " + line + "\n");
				System.out.flush();
				TestData event = TestData.fromString(line);
				long eventTime = getEventTime(event);

				if (prevEventTime != null) {
					long diff = (eventTime - prevEventTime) / servingSpeed;
					Thread.sleep(diff);
				}

				synchronized (lock) {
					eventCnt++;
					sourceContext.collectWithTimestamp(event, eventTime);
					sourceContext.emitWatermark(new Watermark(eventTime - 1));
				}

				prevEventTime = eventTime;
			}
		}

		this.reader.close();
		this.reader = null;
		this.gzipStream.close();
		this.gzipStream = null;

	}

	public long getEventTime(TestData ride) {
		return ride.getEventTime();
	}

	@Override
	public void cancel() {
		try {
			if (this.reader != null) {
				this.reader.close();
			}
			if (this.gzipStream != null) {
				this.gzipStream.close();
			}
		} catch(IOException ioe) {
			throw new RuntimeException("Could not cancel SourceFunction", ioe);
		} finally {
			this.reader = null;
			this.gzipStream = null;
		}
	}

	@Override
	public List<Long> snapshotState(long checkpointId, long checkpointTimestamp) throws Exception {
		return Collections.singletonList(eventCnt);
	}

	@Override
	public void restoreState(List<Long> state) throws Exception {
		for (Long s : state)
			this.eventCnt = s;
	}
}
