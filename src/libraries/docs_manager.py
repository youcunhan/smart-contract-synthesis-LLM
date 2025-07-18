"""
Library Documentation Manager

Manages natural language documentation for common Solidity libraries, providing guidance for LLM usage.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class LibraryDoc(BaseModel):
    """Library documentation model"""
    name: str = Field(..., description="Library name")
    description: str = Field(..., description="Library description")
    functions: List[Dict[str, Any]] = Field(default_factory=list, description="Function list")
    examples: List[str] = Field(default_factory=list, description="Usage examples")
    best_practices: List[str] = Field(default_factory=list, description="Best practices")
    security_notes: List[str] = Field(default_factory=list, description="Security notes")


class LibraryDocsManager:
    """Library documentation manager"""
    
    def __init__(self, docs_dir: str = "src/libraries/docs"):
        self.docs_dir = Path(docs_dir)
        self.docs_dir.mkdir(parents=True, exist_ok=True)
        self.libraries: Dict[str, LibraryDoc] = {}
        self._load_libraries()
    
    def _load_libraries(self):
        """Load all library docs"""
        self._load_builtin_libraries()
        self._load_external_libraries()
    
    def _load_builtin_libraries(self):
        """Load built-in library docs"""
        # SafeMath
        safemath_doc = LibraryDoc(
            name="SafeMath",
            description="SafeMath is a library for safe mathematical operations on uint256, preventing overflows and underflows. Deprecated in Solidity >=0.8.0, but still useful for older contracts.",
            functions=[
                {"name": "add", "description": "Returns the addition of two unsigned integers, reverting on overflow."},
                {"name": "sub", "description": "Returns the subtraction of two unsigned integers, reverting on underflow."},
                {"name": "mul", "description": "Returns the multiplication of two unsigned integers, reverting on overflow."},
                {"name": "div", "description": "Returns the integer division of two unsigned integers, reverting on division by zero."}
            ],
            examples=[
                "using SafeMath for uint256;\nuint256 c = a.add(b);"
            ],
            best_practices=[
                "Use SafeMath for all arithmetic operations in Solidity <0.8.0.",
                "In Solidity >=0.8.0, built-in overflow checks make SafeMath optional."
            ],
            security_notes=[
                "Prevents integer overflows and underflows.",
                "Not needed in Solidity >=0.8.0 unless for explicit clarity."
            ]
        )
        # SafeERC20
        safeerc20_doc = LibraryDoc(
            name="SafeERC20",
            description="SafeERC20 is a wrapper around ERC20 operations that throw on failure (when the token contract returns false). It also supports non-standard ERC20 tokens that do not return a value.",
            functions=[
                {"name": "safeTransfer", "description": "Safely transfers tokens to a specified address."},
                {"name": "safeTransferFrom", "description": "Safely transfers tokens from one address to another."},
                {"name": "safeApprove", "description": "Safely sets the allowance for a spender."},
                {"name": "safeIncreaseAllowance", "description": "Safely increases the allowance for a spender."},
                {"name": "safeDecreaseAllowance", "description": "Safely decreases the allowance for a spender."}
            ],
            examples=[
                "using SafeERC20 for IERC20;\ntoken.safeTransfer(to, amount);"
            ],
            best_practices=[
                "Always use SafeERC20 for token transfers to handle non-standard tokens.",
                "Avoid using approve/transferFrom patterns that are vulnerable to race conditions."
            ],
            security_notes=[
                "Handles tokens that do not return a boolean value.",
                "Prevents loss of funds due to silent failures."
            ]
        )
        # ERC20
        erc20_doc = LibraryDoc(
            name="ERC20",
            description="ERC20 is the standard interface for fungible tokens on Ethereum, supporting transfer, approval, and allowance mechanisms.",
            functions=[
                {"name": "transfer", "description": "Transfers tokens to a specified address."},
                {"name": "approve", "description": "Approves a spender to transfer tokens on behalf of the owner."},
                {"name": "transferFrom", "description": "Transfers tokens from one address to another using allowance."},
                {"name": "balanceOf", "description": "Returns the token balance of an address."},
                {"name": "totalSupply", "description": "Returns the total token supply."}
            ],
            examples=[
                "token.transfer(to, amount);",
                "token.approve(spender, amount);"
            ],
            best_practices=[
                "Implement all required ERC20 functions and events.",
                "Use SafeERC20 for interactions with other tokens."
            ],
            security_notes=[
                "Beware of reentrancy in callbacks.",
                "Check for integer overflows in custom logic."
            ]
        )
        # ReentrancyGuard
        reentrancy_doc = LibraryDoc(
            name="ReentrancyGuard",
            description="ReentrancyGuard is a contract module that helps prevent reentrant calls to a function, commonly used to secure functions that transfer Ether or tokens.",
            functions=[
                {"name": "nonReentrant", "description": "Modifier to prevent a contract from calling itself, directly or indirectly."}
            ],
            examples=[
                "contract MyContract is ReentrancyGuard {\n  function withdraw() public nonReentrant { ... }\n}"
            ],
            best_practices=[
                "Apply nonReentrant to all functions that transfer value out.",
                "Combine with checks-effects-interactions pattern."
            ],
            security_notes=[
                "Prevents reentrancy attacks.",
                "Do not use nonReentrant on functions that call each other."
            ]
        )
        # Ownable
        ownable_doc = LibraryDoc(
            name="Ownable",
            description="Ownable is a contract module that provides basic access control, where there is an account (an owner) that can be granted exclusive access to specific functions.",
            functions=[
                {"name": "onlyOwner", "description": "Modifier to restrict function access to the contract owner."},
                {"name": "transferOwnership", "description": "Transfers contract ownership to a new account."},
                {"name": "renounceOwnership", "description": "Removes the owner, leaving the contract without an owner."}
            ],
            examples=[
                "contract MyContract is Ownable {\n  function mint() public onlyOwner { ... }\n}"
            ],
            best_practices=[
                "Use onlyOwner for all admin functions.",
                "Transfer ownership to a secure address after deployment."
            ],
            security_notes=[
                "Do not leave the contract without an owner unless intended.",
                "Be careful with ownership transfer logic."
            ]
        )
        # Pausable
        pausable_doc = LibraryDoc(
            name="Pausable",
            description="Pausable is a contract module that allows children to implement an emergency stop mechanism that can be triggered by an authorized account.",
            functions=[
                {"name": "whenNotPaused", "description": "Modifier to make a function callable only when the contract is not paused."},
                {"name": "whenPaused", "description": "Modifier to make a function callable only when the contract is paused."},
                {"name": "pause", "description": "Triggers stopped state."},
                {"name": "unpause", "description": "Returns to normal state."}
            ],
            examples=[
                "contract MyContract is Pausable {\n  function foo() public whenNotPaused { ... }\n}"
            ],
            best_practices=[
                "Pause contract during emergencies or upgrades.",
                "Unpause only after thorough review."
            ],
            security_notes=[
                "Ensure only trusted accounts can pause/unpause.",
                "Pausing disables critical functions, use with care."
            ]
        )
        # AccessControl
        accesscontrol_doc = LibraryDoc(
            name="AccessControl",
            description="AccessControl is a role-based access control mechanism, allowing multiple accounts to be granted different roles with specific permissions.",
            functions=[
                {"name": "grantRole", "description": "Grants a role to an account."},
                {"name": "revokeRole", "description": "Revokes a role from an account."},
                {"name": "hasRole", "description": "Checks if an account has a specific role."},
                {"name": "renounceRole", "description": "Account renounces a role it has."}
            ],
            examples=[
                "contract MyContract is AccessControl {\n  bytes32 public constant ADMIN_ROLE = keccak256(\"ADMIN\");\n  function foo() public onlyRole(ADMIN_ROLE) { ... }\n}"
            ],
            best_practices=[
                "Use roles for fine-grained permissions.",
                "Revoke roles from compromised accounts immediately."
            ],
            security_notes=[
                "Roles are managed on-chain, ensure proper governance.",
                "Do not hardcode sensitive roles in public code."
            ]
        )
        # ERC721
        erc721_doc = LibraryDoc(
            name="ERC721",
            description="ERC721 is the standard interface for non-fungible tokens (NFTs) on Ethereum, supporting unique asset ownership and transfer.",
            functions=[
                {"name": "safeTransferFrom", "description": "Safely transfers the ownership of a given token ID to another address."},
                {"name": "ownerOf", "description": "Returns the owner of a given token ID."},
                {"name": "balanceOf", "description": "Returns the number of NFTs owned by an address."},
                {"name": "approve", "description": "Grants or removes permission to transfer a token ID."}
            ],
            examples=[
                "contract MyNFT is ERC721 {\n  function mint(address to, uint256 tokenId) public { ... }\n}"
            ],
            best_practices=[
                "Implement all required ERC721 functions and events.",
                "Use safeTransferFrom to avoid lost tokens."
            ],
            security_notes=[
                "Check for reentrancy in token receivers.",
                "Validate token existence before transfer."
            ]
        )
        # ERC1155
        erc1155_doc = LibraryDoc(
            name="ERC1155",
            description="ERC1155 is a multi-token standard supporting both fungible and non-fungible tokens in a single contract, with batch transfer and approval features.",
            functions=[
                {"name": "safeTransferFrom", "description": "Safely transfers a specific amount of a token ID to another address."},
                {"name": "safeBatchTransferFrom", "description": "Safely transfers multiple token IDs and amounts in a single call."},
                {"name": "balanceOf", "description": "Returns the balance of a specific token ID for an address."},
                {"name": "setApprovalForAll", "description": "Enables or disables approval for a third party to manage all tokens."}
            ],
            examples=[
                "contract MyMultiToken is ERC1155 {\n  function mint(address to, uint256 id, uint256 amount) public { ... }\n}"
            ],
            best_practices=[
                "Use batch operations for gas efficiency.",
                "Implement URI management for metadata."
            ],
            security_notes=[
                "Check for reentrancy in batch transfers.",
                "Validate input arrays for length and correctness."
            ]
        )
        # Chainlink (keep as before, but in English)
        chainlink_doc = LibraryDoc(
            name="Chainlink",
            description="Chainlink provides decentralized oracle services for accessing off-chain data.",
            functions=[
                {"name": "AggregatorV3Interface", "description": "Interface for fetching price data."},
                {"name": "VRFConsumerBase", "description": "Base contract for verifiable random function consumers."}
            ],
            examples=[
                "Get ETH/USD price",
                "Generate verifiable random numbers",
                "Request external data"
            ],
            best_practices=[
                "Verify oracle addresses.",
                "Check the freshness of price data.",
                "Handle oracle failures gracefully."
            ],
            security_notes=[
                "Do not rely on a single oracle.",
                "Check for price deviations.",
                "Set reasonable timeouts."
            ]
        )
        self.libraries = {
            "safemath": safemath_doc,
            "safeerc20": safeerc20_doc,
            "erc20": erc20_doc,
            "reentrancyguard": reentrancy_doc,
            "ownable": ownable_doc,
            "pausable": pausable_doc,
            "accesscontrol": accesscontrol_doc,
            "erc721": erc721_doc,
            "erc1155": erc1155_doc,
            "chainlink": chainlink_doc
        }
    
    def _load_external_libraries(self):
        """Load external library docs from files"""
        for doc_file in self.docs_dir.glob("*.json"):
            try:
                with open(doc_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    library_doc = LibraryDoc(**data)
                    self.libraries[library_doc.name.lower()] = library_doc
            except Exception as e:
                print(f"Failed to load library doc {doc_file}: {e}")
    
    def get_library(self, name: str) -> Optional[LibraryDoc]:
        """Get documentation for a specific library"""
        return self.libraries.get(name.lower())
    
    def get_all_libraries(self) -> List[str]:
        """Get all library names"""
        return list(self.libraries.keys())
    
    def add_library(self, library_doc: LibraryDoc):
        """Add a new library doc"""
        self.libraries[library_doc.name.lower()] = library_doc
        self._save_library(library_doc)
    
    def _save_library(self, library_doc: LibraryDoc):
        """Save library doc to file"""
        doc_file = self.docs_dir / f"{library_doc.name.lower()}.json"
        with open(doc_file, 'w', encoding='utf-8') as f:
            json.dump(library_doc.dict(), f, indent=2, ensure_ascii=False)
    
    def get_library_summary(self, name: str) -> str:
        """Get summary info for a library"""
        library = self.get_library(name)
        if not library:
            return f"Library {name} not found"
        
        summary = f"# {library.name}\n\n"
        summary += f"{library.description}\n\n"
        
        if library.functions:
            summary += "## Main Functions\n"
            for func in library.functions[:3]:
                summary += f"- **{func['name']}**: {func['description']}\n"
            summary += "\n"
        
        if library.best_practices:
            summary += "## Best Practices\n"
            for practice in library.best_practices[:3]:
                summary += f"- {practice}\n"
            summary += "\n"
        
        return summary
    
    def get_relevant_libraries(self, keywords: List[str]) -> List[LibraryDoc]:
        """Find relevant libraries by keywords"""
        relevant_libraries = []
        for library in self.libraries.values():
            text = f"{library.name} {library.description}".lower()
            for keyword in keywords:
                if keyword.lower() in text:
                    relevant_libraries.append(library)
                    break
        return relevant_libraries
    
    def generate_library_prompt(self, sketch_content: str) -> str:
        """Generate library usage prompt based on sketch content"""
        keywords = self._extract_keywords(sketch_content)
        relevant_libraries = self.get_relevant_libraries(keywords)
        if not relevant_libraries:
            return "No relevant library recommendations found."
        prompt = "## Recommended Solidity Libraries\n\n"
        prompt += "Based on your contract needs, the following libraries may be useful:\n\n"
        for library in relevant_libraries:
            prompt += self.get_library_summary(library.name)
            prompt += "\n"
        return prompt
    
    def _extract_keywords(self, content: str) -> List[str]:
        """Extract keywords from content"""
        keywords = []
        if "mapping" in content:
            keywords.append("mapping")
        if "array" in content or "[]" in content:
            keywords.append("array")
        if "math" in content or "+" in content or "-" in content:
            keywords.append("math")
        if "access" in content or "owner" in content:
            keywords.append("access control")
        if "token" in content or "transfer" in content:
            keywords.append("token")
        if "random" in content:
            keywords.append("random")
        if "price" in content or "oracle" in content:
            keywords.append("oracle")
        return keywords 