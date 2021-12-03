# LCW Compression

LCW compression is a proprietary compression used in Westwood Studio's games. This repo's primary aim is to recreate the compression and decompression code in python. 

## About the algorithm:

LCW is also known as format 80 due to the compression format always ends with byte 0x80. 

## Motivation:

To decode the the `[OverlayPack]` and `[OverlayDataPack]` sections in red alert 2 map so that map coordinate translation is possible.