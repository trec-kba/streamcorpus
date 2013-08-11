package test;

import org.apache.thrift.TException;
import org.apache.thrift.protocol.TBinaryProtocol;
import org.apache.thrift.transport.TIOStreamTransport;
import org.apache.thrift.transport.TTransport;
import org.apache.thrift.transport.TTransportException;
import streamcorpus.StreamItem;

import java.io.*;

/**
 * Date: 4/24/13
 */
public final class FilterStreamItems {
    public static void main(String[] args) {
        try {
            processFiles("/home/jacek/Downloads/streamcorpus");
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    private static void processFiles(final String dirPath) throws TException, FileNotFoundException {
        final File dir = new File(dirPath);
        if (dir.exists() && dir.isDirectory()) {
            final FilenameFilter scFilter = new FilenameFilter() {
                @Override
                public boolean accept(final File dir, final String name) {
                    return name.endsWith(".sc");
                }
            };
            final long start = System.currentTimeMillis();
            int siCount = 0;
            int chunkCount = 0;
            long totalBytes = 0;
            for (final File scFile : dir.listFiles(scFilter)) {
                final long fileSize = scFile.length();
                final TTransport transport = new TIOStreamTransport(new BufferedInputStream(new FileInputStream(scFile)));
                final TBinaryProtocol protocol = new TBinaryProtocol(transport);
                transport.open();
                ++chunkCount;
                totalBytes += fileSize;
                try {
                    while (true) {
                        final StreamItem item = new StreamItem();
                        item.read(protocol);
                        ++siCount;
                        if (siCount % 100 == 0) {
                            final long elapsedSec = (System.currentTimeMillis() - start) / 1000;
                            double chunkRate = (double) chunkCount / elapsedSec;
                            double siRate = (double) siCount / elapsedSec;
                            double num_total_stream_items = 5 * Math.pow(10, 8);
                            double remaining_days = num_total_stream_items / siRate / 3600;
                            double remaining_hours = remaining_days / 24;
                            System.out.println(String.format("%d chunks, %d SIs in %.3f seconds --> %.3f chunks/sec, %.3f SIs/sec --> %.1f hours (%.1f days) remaining for %f SIs",
                                    chunkCount, siCount, (float) elapsedSec, (float) chunkRate, (float) siRate, remaining_days, remaining_hours, num_total_stream_items));
                        }
                    }
                } catch (TTransportException te) {
                    if (te.getType() == TTransportException.END_OF_FILE) {
                        System.out.println("*** EOF ***");
                    } else {
                        throw te;
                    }
                }
                transport.close();

                final long end = System.currentTimeMillis();
                System.out.println("msec " + (end - start));
                System.out.println((totalBytes / (end - start) / 1000) + " MB/sec ");
            }
        }
    }
}
