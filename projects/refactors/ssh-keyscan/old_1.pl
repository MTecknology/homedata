#!/usr/bin/perl
#############################################################################
# Scan homedirs for joyous file stuff
#
# This program will take as input a series of files to use.  It will hunt
# for files in a given list of volumes, that either contain the file magic
# specified in the magic types, or match a filename pattern specified in
# the pattern file.
# It will output to the specified outputdir parameter the files, maintaining
# most of the structure
#
# Inputs:
#   - the magic types to search for, one per line
#   - the filename patterns to search for, one per line
#   - the volumes to search, one per line
#   - The output directory (singular)
#
# Outputs:
#   - Will copy the files to the output directory
#
# Assumptions:
#   - Running with full permissions to read/write as required
#############################################################################

####
# Modules used, lots of File modules today
####
use File::MMagic;
use File::Find;
use Getopt::Std;
use File::Copy;
use File::Path qw(make_path);
use File::Basename;

####
# Global Vars
####
our %opts;
our @namepatterns;
our @magic;

####
# Standard usage routine
####
sub usage {
    printf ("$0 [-h] [-f filename] [-t types] [-p patterns] [-o outputdir]\n");
    printf ("%-13s : File containing filename patterns to collect\n","-p filename");
    printf ("%-13s : File containing file magic types to collect\n","-t filename");
    printf ("%-13s : File containing volumes to scan\n","-f filename");
    printf ("%-13s : Directory to copy selected files to\n","-o dirname");
    printf ("%-13s : Just Kidding mode, scan, do not copy\n","-k");
    exit 0;
}

####
# Parse the arguments
####
sub parseargs {
    my %opts;
    getopts('hdf:p:t:o:k',\%opts);

    if ( $opts{h} ) { usage(); }
    return \%opts;
}

####
# Standard debug script
####
sub debug { my $msg=shift;
    if ( $opts{d} ) {
        printf ("DEBUG: |%s|\n",$msg);
    }
}

####
# Read in one of the config files, return the list
# Only using the simplest config, one entry per line, comments ignored
####
sub grabfile {
    my $conffile = shift;
    my $fh;
    my @entry;

    open $fh,$conffile or die "Cannot open $conffile: $!\n";
    while (my $line=<$fh>) {
        $line=~s/^\s+//;
        $line=~s/#.+//;
        $line=~s/\s+$//;
        $line =~ /^$/ && next;

        push @entry, $line; 
    }
    return @entry;
}

####
# The File::Find command requires a wanted subroutine that acts on each
# filename returned.  It calls a capture routine to capture the ones we want
####
sub wanted {
   my $captured=0;
   my $dir=$File::Find::dir;
   my $file=$_;
   
   foreach my $namepat (@namepatterns) {
       if ( $file =~ /$namepat/ ) { 
           capture("$dir/$file");
           $captured=1;
           last;
       }
   } 
   if ( $captured != 1 ) {
        my $ft=File::MMagic->new('/etc/magic');
        my $type=$ft->checktype_filename($file);
        debug ("File:$file\t Type:$type");
        foreach my $magicpat (@magic) {
            if ( $type =~ /$magicpat/ ) {
                capture("$dir/$file");
                $captured=1;
                last;
            }
        }
    }
}

####
# Capture any filename passed to us
####
sub capture {
    my $filename=shift;
    my $destdir="/tmp/outtest";
    my $destfile; 
    my $outdir;

    if ( $opts{o} ) {
        $destdir=$opts{o};
    }
    $destfile = $filename;
    $outdir = dirname ($destfile);
    $outdir =~ s-/homes/--;
    $destfile=basename($filename);
    $destdir="$destdir/$outdir";
    debug ("Capture $filename to $destdir/$destfile");
    if ( ! $opts{k} ) {
        make_path($destdir, {
            chmod=>0700
        });
        copy("$filename","$destdir/$destfile") or warn "Could not copy $filename: $!";
    } else {
        print ("cp $filename\n");
    }
}

####
# Main
####

my $optsptr;
my @volumes;

binmode(STDOUT, ":utf8");

$optsptr=parseargs();
%opts=%$optsptr;

if ( $opts{f} ) {
    @volumes=grabfile($opts{f});
}

if ( $opts{p} ) {
    @namepatterns=grabfile($opts{p});
}

if ( $opts{t} ) {
    @magic=grabfile($opts{t});
}

debug ("Patterns: \n@namepatterns");
debug ("Magic: \n@magic");
debug ("Volumes: \n@volumes");

find (\&wanted, @volumes);
