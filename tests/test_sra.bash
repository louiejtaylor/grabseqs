# test sample listing, metadata download
function test_sra_listing {
    if [ `grabseqs sra -l SRP057027 | wc -l` -ne 369 ]; then
        exit 1
    fi
}

# test metadata download
function test_sra_metadata_downloaded {
    grabseqs sra -m SRP057027.tsv -l -o $TMPDIR/test_metadata/ SRP057027
    if [ `cat $TMPDIR/test_metadata/SRP057027.tsv | wc -l` -ne 370 ] ; then
        exit 1
    fi
    #echo -e "$PASS SRA metadata test passed"
}

# test behavior with -l and --no_parsing
function test_sra_no_parsing_flag {
    if [ `grabseqs sra -l --no_parsing SRR1804203 | wc -l` -ne 1 ]; then
        exit 1
    fi
}

# unpaired fasterq-dump
function test_sra_unpaired {
    grabseqs sra -t 2 -o $TMPDIR/test_tiny_sra ERR2279063
    ls $TMPDIR/test_tiny_sra/ERR2279063.fastq.gz
}

# paired fasterq-dump
function test_sra_paired {
    grabseqs sra -t 2 -o $TMPDIR/test_tiny_sra_paired SRR1913936
    ls $TMPDIR/test_tiny_sra_paired/SRR1913936_1.fastq.gz
    ls $TMPDIR/test_tiny_sra_paired/SRR1913936_2.fastq.gz
}

# unpaired fastq-dump
function test_sra_unpaired_fastqdump {
    grabseqs sra -t 2 -o $TMPDIR/test_fastqdump_sra --use_fastq_dump ERR2279063
    ls $TMPDIR/test_fastqdump_sra/ERR2279063.fastq.gz
}

# paired fasterq-dump
function test_sra_paired_fastqdump {
    grabseqs sra -t 2 -o $TMPDIR/test_fastqdump_sra_paired --use_fastq_dump SRR1913936
    ls $TMPDIR/test_fastqdump_sra_paired/SRR1913936_1.fastq.gz
    ls $TMPDIR/test_fastqdump_sra_paired/SRR1913936_2.fastq.gz
}

# test no clobber
function test_sra_no_clobber {
    t=`grabseqs sra -t 2 -o $TMPDIR/test_fastqdump_sra ERR2279063`
    echo $t
    if [[ $t != *"Pass -f to force download"* ]] ; then
        exit 1
    fi
}

# test force
function test_sra_forced {
    tf=`grabseqs sra -t 2 -o $TMPDIR/test_fastqdump_sra -f ERR2279063`
    echo $tf
    if [[ $tf == *"Pass -f to force download"* ]] ; then
        exit 1
    fi
}

# test custom args to fasterq-dump (#44)
function test_sra_custom_fasterqdump_args {
#    newargs="-f -3"
#    echo runnin with $newargs
    grabseqs sra ERR2279063 -o $TMPDIR/test_fasterqdump_custom --custom_fqdump_args -f -3
    ls $TMPDIR/test_fasterqdump_custom/ERR2279063.fastq.gz
}

# test custom args to fastq-dump
function test_sra_custom_fastqdump_args {
    grabseqs sra ERR2279063 --use_fastq_dump -o $TMPDIR/test_fastqdump_custom --custom_fqdump_args "'--gzip --split-3 --skip-technical'"
    ls $TMPDIR/test_fastqdump_custom/ERR2279063.fastq.gz
}

