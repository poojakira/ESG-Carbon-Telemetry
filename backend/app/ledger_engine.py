import hashlib
import os
from typing import List

class MerkleTree:
    def __init__(self, data_list: List[str]):
        """
        Initializes a Merkle Tree from a list of data strings.
        Each string should be a pre-calculated hash of a ledger record.
        """
        self.leaves = [self._hash(d) for d in data_list]
        self.root = self._build_tree(self.leaves)

    def _hash(self, data: str) -> str:
        if len(data) == 64: # Already a hex hash
             return data
        return hashlib.sha256(data.encode()).hexdigest()

    def _build_tree(self, nodes: List[str]) -> str:
        if not nodes:
            return "0" * 64
        
        if len(nodes) == 1:
            return nodes[0]

        # Ensure even number of nodes by duplicating last if necessary
        if len(nodes) % 2 != 0:
            nodes.append(nodes[-1])

        new_level = []
        for i in range(0, len(nodes), 2):
            combined = nodes[i] + nodes[i+1]
            new_level.append(hashlib.sha256(combined.encode()).hexdigest())

        return self._build_tree(new_level)

    def get_root(self) -> str:
        return self.root

def verify_merkle_batch(data_list: List[str], expected_root: str) -> bool:
    tree = MerkleTree(data_list)
    return tree.get_root() == expected_root

def calculate_audit_signature(root_hash: str, timestamp: str) -> str:
    """ Highly simulated cryptographic signature for industrial audit compliance. """
    payload = f"SIGNATURE-v8|{root_hash}|{timestamp}|{os.getenv('LEDGER_SIGNING_KEY', 'dev-only-key')}"
    return hashlib.sha3_256(payload.encode()).hexdigest()
