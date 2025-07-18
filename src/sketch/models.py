"""
Solidity Sketch Data Models

Defines the data structures for sketch, transaction, and specification.
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


class Specification(BaseModel):
    """Specification definition"""
    pre_condition: str = Field(..., description="Pre-condition")
    post_condition: str = Field(..., description="Post-condition")
    description: Optional[str] = Field(None, description="Specification description")


class Transaction(BaseModel):
    """Transaction definition"""
    name: str = Field(..., description="Function name")
    parameters: List[str] = Field(default_factory=list, description="Parameter list")
    return_type: Optional[str] = Field(None, description="Return type")
    visibility: str = Field("public", description="Visibility")
    spec: Optional[Specification] = Field(None, description="Function specification")
    sketch_code: Optional[str] = Field(None, description="Function sketch code")


class GlobalSpec(BaseModel):
    """Global specification"""
    invariants: List[str] = Field(default_factory=list, description="Invariants")
    constraints: List[str] = Field(default_factory=list, description="Constraints")
    assumptions: List[str] = Field(default_factory=list, description="Assumptions")


class Sketch(BaseModel):
    """Solidity Sketch"""
    contract_name: str = Field(..., description="Contract name")
    imports: List[str] = Field(default_factory=list, description="Import statements")
    state_variables: List[str] = Field(default_factory=list, description="State variables")
    structs: List[str] = Field(default_factory=list, description="Struct definitions")
    events: List[str] = Field(default_factory=list, description="Event definitions")
    transactions: List[Transaction] = Field(default_factory=list, description="Transaction list")
    global_spec: GlobalSpec = Field(default_factory=GlobalSpec, description="Global specification")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata")
    
    def get_transaction_by_name(self, name: str) -> Optional[Transaction]:
        """Get transaction by name"""
        for tx in self.transactions:
            if tx.name == name:
                return tx
        return None
    
    def validate(self) -> bool:
        """Validate the sketch"""
        # Check contract name
        if not self.contract_name or not self.contract_name.strip():
            return False
        
        # Check transaction list
        if not self.transactions:
            return False
        
        # Check transaction name uniqueness
        names = [tx.name for tx in self.transactions]
        if len(names) != len(set(names)):
            return False
        
        return True 