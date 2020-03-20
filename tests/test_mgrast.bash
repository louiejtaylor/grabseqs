# test sample listing, metadata download
function test_mgrast_listing {
if [ `grabseqs mgrast -l mgp85479 | wc -l` -ne 4 ]; then
    exit 1
fi
}

# test metadata
function test_mgrast_metadata {
    grabseqs mgrast -o $TMPDIR/test_md_mg -m META.csv -l mgp85479
    if [ `cat $TMPDIR/test_md_mg/META.csv | wc -l` -ne 5 ] ; then
        exit 1
    fi
}

# download a tiny sample, .fastq-formatted
function test_mgrast_fastq {
    grabseqs mgrast -o $TMPDIR/test_tiny_mg mgm4793571.3
    ls $TMPDIR/test_tiny_mg/mgm4793571.3.fastq.gz
}

## download a tiny sample, .fasta-formatted
function test_mgrast_fasta {
    grabseqs mgrast -o $TMPDIR/test_tiny_mg_fasta mgm4440055.3
    ls $TMPDIR/test_tiny_mg_fasta/mgm4440055.3.fastq.gz
}

## test no clobber
function test_mgrast_fastq_noclobber {
    u=`grabseqs mgrast -o $TMPDIR/test_tiny_mg mgm4793571.3`
    echo $u
    if [[ $u != *"Pass -f to force download"* ]] ; then
        exit 1
    fi
}

## test force
function test_mgrast_fastq_force_download {
    u=`grabseqs mgrast -o $TMPDIR/test_tiny_mg -f mgm4793571.3`
    echo $u
    if [[ $u == *"Pass -f to force download"* ]] ; then
        exit 1
    fi
    ls $TMPDIR/test_tiny_mg/mgm4793571.3.fastq.gz
}

