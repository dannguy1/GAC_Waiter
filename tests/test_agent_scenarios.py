"""
Integration tests for WaitstaffAgent scenarios.
Tests critical workflows: Anti-hallucination, Allergy recording, and Order taking.
"""

import pytest
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.agent import WaitstaffAgent

class TestAgentScenarios:
    
    @pytest.fixture
    def agent(self):
        """Create an agent instance for testing."""
        return WaitstaffAgent()

    def test_hallucination_prevention(self, agent):
        """
        Test that the agent does not recommend or add items not on the menu.
        Scenario: User asks for 'Sushi', which is not in the menu.
        """
        messages = [{"role": "user", "content": "Can I order the Sushi Roll?"}]
        result = agent.run(messages)
        
        # 1. No items should be mentioned/suggested because none should be found.
        # (Assuming Sushi is definitely not in the Vector DB)
        sushi_mentions = [i for i in result['mentioned_items'] if 'sushi' in i['item_name'].lower()]
        assert len(sushi_mentions) == 0, "Agent hallucinated Sushi items"
        
        # 2. Cart should be empty
        assert len(result['cart_updates']) == 0, "Agent added non-existent item to cart"
        
        # 3. Text should likely apologize or say not found
        # (This is soft assertion, mainly checking system logic didn't hallucinate an Action: add_to_cart)

    def test_allergy_note_recording(self, agent):
        """
        Test that the agent correctly records allergies using set_general_note.
        Scenario: User states peanut allergy.
        """
        messages = [{"role": "user", "content": "I am allergic to peanuts."}]
        result = agent.run(messages)
        
        # Verify general_note was populated
        note = result.get('general_note')
        assert note is not None, "Allergy note was NOT set"
        assert "peanut" in note.lower(), "Note content mismatch"

    def test_add_to_cart(self, agent):
        """
        Test that valid items are correctly added to the cart.
        Scenario: User orders 'Egg rolls'.
        """
        messages = [{"role": "user", "content": "I would like to order one order of Egg rolls, please."}]
        result = agent.run(messages)
        
        # Verify cart update
        updates = result.get('cart_updates')
        assert len(updates) > 0, "Cart should have items"
        
        item = updates[0]
        # Check fuzzy match or exact name
        assert "egg roll" in item['name'].lower(), "Item name should contain Egg Roll"
        assert item['qty'] == 1, "Quantity should be 1"

    def test_vietnamese_recommendation(self, agent):
        """
        Test that items are correctly identified when discussed in Vietnamese.
        Scenario: Agent discusses 'Cá Nướng Da Giòn' (Baked Crispy Catfish).
        """
        # Setup a fake item that has a long Vietnamese name
        long_name_item = {
            "item_name": "Baked Crispy Catfish with Boiled Pork",
            "item_viet": "Cá Nướng Da Giòn Thịt Luộc",
            "price": 22
        }
        
        # Scenario 1: Agent uses the full name (Exact match)
        content_full = "Chúng tôi có Cá Nướng Da Giòn Thịt Luộc rất ngon."
        result_full = agent._filter_mentioned_items(content_full, [long_name_item])
        assert len(result_full) == 1, "Should match full Vietnamese name"
        
        # Scenario 2: Agent uses a natural shortened version (Prefix match)
        # "Cá Nướng Da Giòn" is the first 4 words.
        content_short = "Bạn nên thử món Cá Nướng Da Giòn của chúng tôi."
        result_short = agent._filter_mentioned_items(content_short, [long_name_item])
        assert len(result_short) == 1, "Should match shortened Vietnamese name (Prefix)"
        
        # Scenario 3: Agent uses a completely different incompatible name
        content_wrong = "Bạn nên thử món Bún Bò Huế."
        result_wrong = agent._filter_mentioned_items(content_wrong, [long_name_item])
        assert len(result_wrong) == 0, "Should NOT match unrelated text"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
