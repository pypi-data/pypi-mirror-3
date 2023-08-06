#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Converts file fed in into hms, dms format
#

from astLib import astCoords
import sys

# Main
if len(sys.argv) < 8:
    print "Run: % coordConvert.py <in file> <out file> <RA column> <dec column> <way [either \"to_decimal\" or \"to_hmsdms\"]> <coord delimiter> <output column delimiter [e.g. \"tab\" \",\" \"&\" etc.]>"
else:
    
    inFile=sys.argv[1]
    outFile=sys.argv[2]
    RACol=int(sys.argv[3])-1
    decCol=int(sys.argv[4])-1
    way=sys.argv[5]
    delimiter=sys.argv[6]
    colDelim=str(sys.argv[7]).rstrip("\n")
    
    if colDelim=="tab":
        colDelim="\t"
    
    wayOk=False
    if way=="to_decimal":
        wayOk=True
    if way=="to_hmsdms":
        wayOk=True
    if wayOk==False:
        print "<way>: either \"to_decimal\" or \"to_hmsdms\""
        sys.exit()
    
    reader=file(inFile, "rb")
    lines=reader.readlines()
    reader.close()
    
    writer=file(outFile, "wb")
    for row in lines:
        if len(row)>1:
            if "#" not in row[:1]:
                rowBits=row.split("\t")
                if way=="to_decimal":
                    RADeg=astCoords.hms2decimal(rowBits[RACol], delimiter)
                    decDeg=astCoords.dms2decimal(rowBits[decCol], delimiter)
                if way=="to_hmsdms":
                    RADeg=astCoords.decimal2hms(float(rowBits[RACol]), delimiter)
                    decDeg=astCoords.decimal2dms(float(rowBits[decCol]), delimiter)
                writeString=""
                for i in range(len(rowBits)):
                    if i==RACol:
                        writeString=writeString+str(RADeg)+"\t"
                    elif i==decCol:
                        writeString=writeString+str(decDeg)+"\t"
                    elif rowBits[i].find("\n")!=-1:
                        writeString=writeString+str(rowBits[i])
                    else:
                        writeString=writeString+str(rowBits[i])+"\t"
                writer.write(writeString.replace("\n", "").replace("\t", colDelim)+"\n")	# new line character already included	
            else:
                writer.write(row.replace("\t", colDelim))
    writer.close()

#----------------------------------------------------------------------------------------------------------
