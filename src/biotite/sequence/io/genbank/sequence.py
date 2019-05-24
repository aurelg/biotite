# This source code is part of the Biotite package and is distributed
# under the 3-Clause BSD License. Please see 'LICENSE.rst' for further
# information.

"""
Functions for converting a sequence from/to a GenBank file.
"""

__author__ = "Patrick Kunzmann"
__all__ = ["get_sequence", "get_annotated_sequence",
           "set_sequence", "set_annotated_sequence"]

import re
from ....file import InvalidFileError
from ...seqtypes import ProteinSequence, NucleotideSequence
from ...annotation import AnnotatedSequence
from .file import GenBankFile
from .annotation import get_annotation, set_annotation


_SYMBOLS_PER_CHUNK = 10
_SEQ_CHUNKS_PER_LINE = 6
_SYMBOLS_PER_LINE = _SYMBOLS_PER_CHUNK * _SEQ_CHUNKS_PER_LINE


def get_sequence(gb_file, format="gb"):
    """
    Get the sequence from the *ORIGIN* field of a GenBank file.

    Parameters
    ----------
    format : {'gb', 'gp'}
        Indicates whether the file is a GenBank or a GenPept file.
        Depending on this parameter a `NucleotideSequence` or a
        `ProteinSequence` is returned.
    
    Returns
    -------
    sequence : NucleotideSequence or ProteinSequence
        The reference sequence in the file.
    """
    fields = gb_file.get_fields("ORIGIN")
    if len(fields) == 0:
        raise InvalidFileError("File has no 'ORIGIN' field")
    if len(fields) > 1:
        raise InvalidFileError("File has multiple 'ORIGIN' fields")
    lines, _ = fields[0]
    seq_str = _field_to_seq_string(lines)
    return _convert_seq_str(seq_str, format)


def get_annotated_sequence(gb_file, format="gb", include_only=None):
    """
    Get an annotated sequence by combining the *ANNOTATION* and
    *ORIGIN* fields of a GenBank file.
    
    Parameters
    ----------
    include_only : iterable object, optional
        List of names of feature keys (`str`), which should included
        in the annotation. By default all features are included.
    
    Returns
    ----------
    annot_seq : AnnotatedSequence
        The annotated sequence.
    """
    fields = gb_file.get_fields("ORIGIN")
    if len(fields) == 0:
        raise InvalidFileError("File has no 'ORIGIN' field")
    if len(fields) > 1:
        raise InvalidFileError("File has multiple 'ORIGIN' fields")
    lines, _ = fields[0]
    seq_str = _field_to_seq_string(lines)
    sequence = _convert_seq_str(seq_str, format)
    seq_start = _get_seq_start(lines)
    annotation = get_annotation(gb_file, include_only)
    return AnnotatedSequence(annotation, sequence, sequence_start=seq_start)


def set_sequence(gb_file, sequence, sequence_start=1):
    lines = []
    seq_str = str(sequence)
    line = "{:>9d}".format(sequence_start)
    for i in range(0, len(sequence), _SYMBOLS_PER_CHUNK):
        # New line after 5 sequence chunks
        if i != 0 and i % _SYMBOLS_PER_LINE == 0:
            lines.append(line)
            line = "{:>9d}".format(sequence_start + i)
        line += " " + str(seq_str[i : i + _SYMBOLS_PER_CHUNK])
    # Append last line
    lines.append(line)

    indices = gb_file.get_indices("ORIGIN")
    if len(indices) > 1:
        raise InvalidFileError("File contains multiple 'ORIGIN' fields")
    elif len(indices) == 1:
        # Replace existing entry
        index = indices[0]
        gb_file[index] = "ORIGIN", lines
    else:
        # Add new entry as no entry exists yet
        gb_file.append("ORIGIN", lines)


def set_annotated_sequence(gb_file, annot_sequence):
    set_annotation(gb_file, annot_sequence.annotation)
    set_sequence(
        gb_file, annot_sequence.sequence, annot_sequence.sequence_start
    )
    


def _field_to_seq_string(origin_content):
    seq_str = "".join(origin_content)
    # Remove numbers and emtpy spaces
    regex = re.compile("[0-9]| ")
    seq_str = regex.sub("", seq_str)
    return seq_str


def _convert_seq_str(seq_str, format):
    if len(seq_str) == 0:
        raise InvalidFileError("The file's 'ORIGIN' field is empty")
    if format == "gb":
        return NucleotideSequence(seq_str)
    elif format == "gp":
        return ProteinSequence(seq_str)
    else:
        raise ValueError(f"Unknown format '{format}'")
    

def _get_seq_start(origin_content):
    # Start of sequence is the sequence position indicator
    # at the beginning of the first line
    return int(origin_content[0].split()[0])