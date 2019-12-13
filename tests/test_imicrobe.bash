# test sample listing and metadata download
function test_imicrobe_listing_project {
    if [ `grabseqs imicrobe -l p1 | wc -l` -ne 2 ]; then
        exit 1
    fi
}

# test metadata download
function test_imicrobe_metadata_download {
    grabseqs imicrobe -o $TMPDIR/test_md_im -m META.csv -l p1
    if [ `cat $TMPDIR/test_md_im/META.csv | wc -l` -ne 3 ] ; then
        exit 1
    fi
}

# paired sample listing
function test_imicrobe_listing_paired_sample {
ps=`grabseqs imicrobe -l s6398`
echo $ps
if [ "$ps" != "s6398_1.fastq.gz,s6398_2.fastq.gz" ]; then
    exit 1
fi
}

# download a tiny sample, .fasta-formatted
function test_imicrobe_fasta {
    grabseqs imicrobe -o $TMPDIR/test_tiny_im s710
    ls $TMPDIR/test_tiny_im/s710.fastq.gz
}

# download a tiny sample, .fastq-formatted paired
function test_imicrobe_fastq_paired {
    grabseqs imicrobe -o $TMPDIR/test_tiny_im s6399
    ls $TMPDIR/test_tiny_im/s6399_1.fastq.gz
    ls $TMPDIR/test_tiny_im/s6399_2.fastq.gz
    echo -e "$PASS iMicrobe fastq-formatted sample download test passed"
}

## test no clobber
function test_imicrobe_no_clobber {
    t=`grabseqs imicrobe -t 2 -o $TMPDIR/test_tiny_im s710`
    echo $t
    if [[ $t != *"Pass -f to force download"* ]] ; then
         exit 1
    fi
}

## test force
function test_imicrobe_fasta_force {
    tf=`grabseqs imicrobe -t 2 -o $TMPDIR/test_tiny_im -f s710`
    echo $tf
    if [[ $tf == *"Pass -f to force download"* ]] ; then
        exit 1
    fi
    ls $TMPDIR/test_tiny_im/s710.fastq.gz
}
