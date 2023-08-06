#
# Copyright John Reid 2012
#


"""
Some utilities.
"""

from functools import partial
import sys, corebio.seq


def shorten(seq, length):
    "Shorten the sequence to the given length."
    tag = '(shortened to %d)' % length
    if length > len(seq):
        raise ValueError('Sequence is too short: %d < %d' % (len(seq), length))
    return corebio.seq.Seq(
        seq[:length],
        name='%s %s' % (seq.name, tag),
        description='%s %s' % (seq.description, tag),
        alphabet=seq.alphabet,
    )


def strip_Ns(seq):
    "Strip Ns from beginning and end of the sequences."
    tag = '(stripped of Ns)'
    return corebio.seq.Seq(
        seq.strip('N'),
        name='%s (stripped of Ns)' % seq.name,
        description='%s (stripped of Ns)' % seq.description,
        alphabet=seq.alphabet,
    )


def open_fasta(fasta, default, mode):
    "Open a FASTA file or return default if fasta filename is '-'"
    if '-' == fasta:
        return default
    else:
        return open(fasta, mode)
   
open_input = partial(open_fasta, default=sys.stdin, mode='r')
open_output = partial(open_fasta, default=sys.stdout, mode='w')
