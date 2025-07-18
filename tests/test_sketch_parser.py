"""
Sketch Parser Tests
"""

import pytest
from pathlib import Path
import sys

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.sketch.parser import SketchParser
from src.sketch.models import Sketch, Transaction, Specification


class TestSketchParser:
    """Sketch Parser Test Class"""
    
    def setup_method(self):
        """Setup test environment"""
        self.parser = SketchParser()
    
    def test_parse_contract_name(self):
        """Test parsing contract name"""
        content = """
        contract TestContract {
            // Contract content
        }
        """
        sketch = self.parser.parse_content(content)
        assert sketch.contract_name == "TestContract"
    
    def test_parse_state_variables(self):
        """Test parsing state variables"""
        content = """
        contract TestContract {
            uint256 public totalSupply;
            mapping(address => uint256) public balanceOf;
            string public name;
        }
        """
        sketch = self.parser.parse_content(content)
        assert len(sketch.state_variables) >= 3
        assert "uint256 public totalSupply;" in sketch.state_variables
        assert "mapping(address => uint256) public balanceOf;" in sketch.state_variables
    
    def test_parse_structs(self):
        """Test parsing structs"""
        content = """
        contract TestContract {
            struct User {
                uint256 id;
                string name;
                bool active;
            }
        }
        """
        sketch = self.parser.parse_content(content)
        assert len(sketch.structs) == 1
        assert "struct User" in sketch.structs[0]
    
    def test_parse_events(self):
        """Test parsing events"""
        content = """
        contract TestContract {
            event Transfer(address indexed from, address indexed to, uint256 value);
            event Approval(address indexed owner, address indexed spender, uint256 value);
        }
        """
        sketch = self.parser.parse_content(content)
        assert len(sketch.events) == 2
        assert "event Transfer" in sketch.events[0]
        assert "event Approval" in sketch.events[1]
    
    def test_parse_functions(self):
        """Test parsing functions"""
        content = """
        contract TestContract {
            function transfer(address to, uint256 amount) public returns (bool) {
                // Function body
            }
            
            function approve(address spender, uint256 amount) public returns (bool) {
                // Function body
            }
        }
        """
        sketch = self.parser.parse_content(content)
        assert len(sketch.transactions) == 2
        
        # Check first function
        assert sketch.transactions[0].name == "transfer"
        assert "address to" in sketch.transactions[0].parameters[0]
        assert "uint256 amount" in sketch.transactions[0].parameters[1]
        assert sketch.transactions[0].return_type == "bool"
        assert sketch.transactions[0].visibility == "public"
        
        # Check second function
        assert sketch.transactions[1].name == "approve"
        assert "address spender" in sketch.transactions[1].parameters[0]
        assert "uint256 amount" in sketch.transactions[1].parameters[1]
    
    def test_parse_specifications(self):
        """Test parsing specifications"""
        content = """
        contract TestContract {
            //@global invariant: totalSupply >= 0
            //@global constraint: balanceOf[address] >= 0
            
            function transfer(address to, uint256 amount) public returns (bool) {
                //@function transfer pre: to != address(0) && balanceOf[msg.sender] >= amount
                //@function transfer post: balanceOf[msg.sender] == old(balanceOf[msg.sender]) - amount
                // Function body
            }
        }
        """
        sketch = self.parser.parse_content(content)
        
        # Check global specifications
        assert len(sketch.global_spec.invariants) == 1
        assert "totalSupply >= 0" in sketch.global_spec.invariants[0]
        
        assert len(sketch.global_spec.constraints) == 1
        assert "balanceOf[address] >= 0" in sketch.global_spec.constraints[0]
        
        # Check function specifications
        transfer_func = sketch.get_transaction_by_name("transfer")
        assert transfer_func is not None
        assert transfer_func.spec is not None
        assert "to != address(0) && balanceOf[msg.sender] >= amount" in transfer_func.spec.pre_condition
        assert "balanceOf[msg.sender] == old(balanceOf[msg.sender]) - amount" in transfer_func.spec.post_condition
    
    def test_parse_complete_contract(self):
        """Test parsing complete contract"""
        content = """
        contract CompleteContract {
            // State variables
            uint256 public totalSupply;
            mapping(address => uint256) public balanceOf;
            
            // Struct
            struct User {
                uint256 id;
                string name;
            }
            
            // Event
            event Transfer(address indexed from, address indexed to, uint256 value);
            
            // Global specification
            //@global invariant: totalSupply >= 0
            
            // Function
            function transfer(address to, uint256 amount) public returns (bool) {
                //@function transfer pre: to != address(0)
                //@function transfer post: balanceOf[to] > old(balanceOf[to])
                require(to != address(0), "Invalid recipient");
                balanceOf[to] += amount;
                emit Transfer(msg.sender, to, amount);
                return true;
            }
        }
        """
        sketch = self.parser.parse_content(content)
        
        # Check all components are parsed correctly
        assert sketch.contract_name == "CompleteContract"
        assert len(sketch.state_variables) >= 2
        assert len(sketch.structs) == 1
        assert len(sketch.events) == 1
        assert len(sketch.transactions) == 1
        assert len(sketch.global_spec.invariants) == 1
        
        # Check function
        transfer_func = sketch.get_transaction_by_name("transfer")
        assert transfer_func is not None
        assert transfer_func.spec is not None
        assert "to != address(0)" in transfer_func.spec.pre_condition
        assert "balanceOf[to] > old(balanceOf[to])" in transfer_func.spec.post_condition
    
    def test_parse_file(self, tmp_path):
        """Test parsing from file"""
        # Create temporary sketch file
        sketch_file = tmp_path / "test_sketch.txt"
        sketch_content = """
        contract TestContract {
            uint256 public value;
            
            function setValue(uint256 newValue) public {
                value = newValue;
            }
        }
        """
        sketch_file.write_text(sketch_content)
        
        # Parse file
        sketch = self.parser.parse_file(str(sketch_file))
        assert sketch.contract_name == "TestContract"
        assert len(sketch.state_variables) == 1
        assert len(sketch.transactions) == 1
        assert sketch.transactions[0].name == "setValue"


if __name__ == "__main__":
    pytest.main([__file__]) 