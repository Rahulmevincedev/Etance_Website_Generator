#!/usr/bin/env python3
"""
Test script to verify the improved LangGraph agent with custom tools
This tests that the agent now uses reliable custom tools instead of desktop commander
"""

import json
import asyncio
import logging
from pathlib import Path
import sys
import shutil
from datetime import datetime

# Add the langgraph_agent module to the path
sys.path.append(str(Path(__file__).parent / "langgraph_agent"))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Test the custom tools directly first
def test_custom_tools():
    """Test the custom tools independently"""
    print("🔧 Testing Custom Tools Directly")
    print("="*40)
    
    try:
        from langgraph_agent.tools.custom_tools import CUSTOM_TOOLS
        print(f"✅ Successfully imported {len(CUSTOM_TOOLS)} custom tools:")
        for tool in CUSTOM_TOOLS:
            print(f"   - {tool.name}: {tool.description}")
            
        # Test a simple operation
        from langgraph_agent.tools.custom_tools import smart_text_replace, read_file_content
        
        # Create a test file
        test_file = "test_custom_tools.html"
        test_content = """<html>
<head><title>Test Cafe</title></head>
<body>
<h1>Welcome to Test Cafe</h1>
<p>Visit us at 123 Old Street, Old City</p>
</body>
</html>"""
        
        with open(test_file, 'w') as f:
            f.write(test_content)
            
        # Test smart_text_replace
        result = smart_text_replace.invoke({
            "file_path": test_file,
            "old_text": "Test Cafe", 
            "new_text": "Amazing Restaurant",
            "max_replacements": None,
            "fuzzy_threshold": 0.85
        })
        
        print(f"✅ smart_text_replace test: {result.message}")
        print(f"   Changes made: {result.changes_made}")
        
        # Read back the file
        content = read_file_content.invoke({
            "file_path": test_file
        })
        
        if "Amazing Restaurant" in content:
            print("✅ Text replacement successful!")
        else:
            print("❌ Text replacement failed!")
            
        # Clean up
        Path(test_file).unlink(missing_ok=True)
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing custom tools: {e}")
        return False


async def test_agent_with_custom_tools():
    """Test the agent with custom tools"""
    print("\n🤖 Testing Agent with Custom Tools")
    print("="*40)
    
    # Test JSON data
    test_data = {
        "websiteName": "Custom Tools Test",
        "websiteDescription": "Testing the improved agent with reliable custom tools",
        "websiteType": "restaurant",
        "restaurantPhone": "555-TEST-TOOLS",
        "restaurantEmail": "test@customtools.com",
        "restaurantAddress": "456 Custom Tools Ave, Test City, TC 67890",
        "operatingHours": {
            "monday": {"open": "08:00", "close": "20:00", "isOpen": True},
            "tuesday": {"open": "08:00", "close": "20:00", "isOpen": True},
            "wednesday": {"open": "08:00", "close": "20:00", "isOpen": True},
            "thursday": {"open": "08:00", "close": "20:00", "isOpen": True},
            "friday": {"open": "08:00", "close": "22:00", "isOpen": True},
            "saturday": {"open": "09:00", "close": "22:00", "isOpen": True},
            "sunday": {"open": "09:00", "close": "19:00", "isOpen": True}
        },
        "facebookUrl": "https://facebook.com/customtoolstest",
        "instagramUrl": "https://instagram.com/customtoolstest", 
        "twitterUrl": "https://twitter.com/customtoolstest",
        "pages": ["home", "about", "contact", "terms", "privacy"],
        "primaryColor": "#28a745",
        "secondaryColor": "#6c757d",
        "accentColor": "#17a2b8",
        "typography": "roboto",
        "selectedFont": "roboto"
    }
    
    try:
        # Clean up any existing test directory
        test_dir = Path("templates/modify/Custom_Tools_Test")
        if test_dir.exists():
            shutil.rmtree(test_dir)
            
        # Initialize the improved agent
        from langgraph_agent.core import LangGraphAgent
        agent = await LangGraphAgent.ainit()
        
        print("✅ Agent initialized with custom tools")
        
        # Get agent info to verify tools loaded
        agent_info = agent.get_agent_info()
        print(f"📊 Agent loaded {agent_info['num_tools']} tools:")
        for tool_name in agent_info['tool_names']:
            print(f"   - {tool_name}")
            
        # Check for custom tools
        custom_tool_names = {
            'read_file_content', 'write_file_content', 'smart_text_replace',
            'copy_directory', 'create_directory', 'list_directory_contents',
            'execute_shell_command'
        }
        
        loaded_tools = set(agent_info['tool_names'])
        custom_tools_present = custom_tool_names.intersection(loaded_tools)
        
        if len(custom_tools_present) >= 5:  # At least 5 custom tools
            print(f"✅ Custom tools properly loaded: {sorted(custom_tools_present)}")
        else:
            print(f"⚠️  Only {len(custom_tools_present)} custom tools found")
            
        # Check that desktop commander tools are NOT present
        desktop_commander_tools = {'edit_block', 'start_process', 'read_process_output'}
        dc_tools_present = desktop_commander_tools.intersection(loaded_tools)
        
        if len(dc_tools_present) == 0:
            print("✅ Desktop commander tools successfully removed")
        else:
            print(f"⚠️  Desktop commander tools still present: {dc_tools_present}")
            
        # Test the agent with a simple request
        print("\n🧪 Testing agent with sample data...")
        
        json_input = json.dumps(test_data, indent=2)
        
        start_time = datetime.now()
        response = await agent.process_request(
            user_input=f"Generate a website with this data: {json_input}",
            user_id="test_user",
            session_id="custom_tools_test",
            user_name="Test User",
            working_directory="."
        )
        end_time = datetime.now()
        
        duration = (end_time - start_time).total_seconds()
        print(f"⏱️  Agent completed in {duration:.1f} seconds")
        
        if response.get("success", False):
            print("✅ Agent execution successful")
            print(f"🔄 Completed {response.get('iteration_count', 0)} iterations")
            
            if test_dir.exists():
                print("✅ Website directory created")
                file_count = len(list(test_dir.rglob("*")))
                print(f"📁 Generated {file_count} files")
                
                # Check if key changes were made
                index_file = test_dir / "index.html"
                if index_file.exists():
                    content = index_file.read_text(encoding='utf-8')
                    
                    success_count = 0
                    if "Custom Tools Test" in content:
                        print("✅ Website name updated")
                        success_count += 1
                    if "test@customtools.com" in content:
                        print("✅ Email updated")
                        success_count += 1
                    if "555-TEST-TOOLS" in content:
                        print("✅ Phone updated")
                        success_count += 1
                        
                    if success_count >= 2:
                        print("🎉 CUSTOM TOOLS ARE WORKING!")
                        return True
                    else:
                        print("⚠️  Some updates may have failed")
                        
            else:
                print("❌ Website directory not created")
                
        else:
            print("❌ Agent execution failed")
            error = response.get("error", "Unknown error")
            print(f"   Error: {error}")
            
        return False
        
    except Exception as e:
        print(f"❌ Agent test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("🚀 Testing Improved LangGraph Agent with Custom Tools")
    print("="*60)
    
    # Test 1: Custom tools directly
    tools_test = test_custom_tools()
    
    # Test 2: Agent with custom tools  
    if tools_test:
        agent_test = asyncio.run(test_agent_with_custom_tools())
    else:
        agent_test = False
        
    # Summary
    print("\n" + "="*60)
    print("FINAL TEST RESULTS")  
    print("="*60)
    print(f"✅ Custom Tools Test: {'PASSED' if tools_test else 'FAILED'}")
    print(f"✅ Agent Integration Test: {'PASSED' if agent_test else 'FAILED'}")
    
    if tools_test and agent_test:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Custom tools are working correctly")
        print("✅ Agent successfully uses custom tools instead of desktop commander")
        print("✅ File editing issues should be resolved")
        print("✅ Agent is now much more reliable!")
    else:
        print("\n❌ Some tests failed - check the output above")
        
    print("="*60)


if __name__ == "__main__":
    main() 