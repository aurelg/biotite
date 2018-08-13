# This source code is part of the Biotite package and is distributed
# under the 3-Clause BSD License. Please see 'LICENSE.rst' for further
# information.

import numpy as np
from enum import IntEnum
from ..copyable import Copyable
from typing import Optional, Tuple, overload, MutableSequence, Union


class BondType(IntEnum):
    ANY = ...
    SINGLE = ...
    DOUBLE = ...
    TRIPLE = ...
    QUADRUPLE = ...
    AROMATIC = ...


class BondList(Copyable):
    def __init__(
        self, atom_count : int, bonds : Optional[np.ndarray] = None
    ) -> None: ...
    def offset_indices(self, offset : int) -> None: ...
    def as_array(self) -> np.ndarray: ...
    def get_atom_count(self) -> int: ...
    def get_bond_count(self) -> int: ...
    def get_bonds(self, atom_index : int) -> Tuple[np.ndarray, np.ndarray]: ...
    def add_bond(
        self, index1 : int, index2 : int, bond_type : BondType = BondType.ANY
    ) -> None: ...
    def remove_bond(self, index1 : int, index2 : int) -> None: ...
    def remove_bonds(self, bond_listBondList : BondList) -> None: ...
    def merge(self, bond_list : BondList) -> None: ...
    def __add__(self, bond_list : BondList) -> None: ...
    @overload
    def __getitem__(self, index: int) -> np.ndarray: ...
    @overload
    def __getitem__(
        self, index: Union[MutableSequence[int], MutableSequence[bool], slice]
    ) -> BondList: ...