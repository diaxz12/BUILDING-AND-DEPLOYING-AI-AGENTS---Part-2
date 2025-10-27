"""
GUARDRAILS EXAMPLE: Creating Custom Validators

This example demonstrates how to create your own custom validation logic
alongside built-in validators from the Guardrails Hub.

USE CASE:
We're building a kid-friendly chatbot that needs to:
1. Block specific "playground insult" words (custom validator)
2. Detect general toxic language using ML (built-in validator)

WHY CREATE CUSTOM VALIDATORS:
- Domain-specific rules: Every application has unique requirements
- Business logic: Enforce company-specific policies
- Simple rules: Sometimes regex or word lists are faster than ML
- Combine approaches: Use both rule-based and ML-based validation
- Full control: Define exactly what should be blocked

LEARNING OBJECTIVES:
- Understand the validator decorator pattern
- Learn how to combine custom and built-in validators
- See when to use custom vs. pre-built validators
- Practice creating reusable validation components
"""

# =============================================================================
# PART 1: Creating a Custom Validator
# =============================================================================

from typing import Dict
from guardrails.validators import (
    FailResult,
    PassResult,
    register_validator,
    ValidationResult,
)
from guardrails import Guard, OnFailAction
from guardrails.hub import ToxicLanguage

print("=" * 70)
print("CREATING A CUSTOM VALIDATOR")
print("=" * 70)

toxic_word_list = ["butt", "poop", "booger", "stupid", "dumb", "idiot"]

# The @register_validator decorator makes this function available as a validator
# - name: How you'll reference this validator (kebab-case by convention)
# - data_type: What type of data this validates ("string", "integer", "list", etc.)
@register_validator(name="toxic-words", data_type="string")
def toxic_words(value: str, metadata: Dict) -> ValidationResult:
    """
    Custom validator to detect playground insult words.
    
    This is a simple rule-based validator that checks for specific words.
    Use this approach when:
    - You have a known list of blocked terms
    - Rules are simple and deterministic
    - You need fast, predictable results
    - Domain-specific terminology needs blocking
    
    Args:
        value: The text to validate (automatically passed by Guardrails)
        metadata: Additional context (provided by the Guard framework)
    
    Returns:
        PassResult: If no toxic words found
        FailResult: If toxic words detected, with error message
    """
    
    # Define your word list - customize based on your needs
    # For a kid-friendly app, we block common playground insults
    toxic_word_list = ["butt", "poop", "booger", "stupid", "dumb", "idiot"]
    
    # Track which words were found (for detailed error messages)
    mentioned_words = []
    
    # Case-insensitive search through the text
    value_lower = value.lower()
    for word in toxic_word_list:
        if word in value_lower:
            mentioned_words.append(word)
    
    # Return validation result
    if len(mentioned_words) > 0:
        # FailResult: Validation failed
        # - Provide clear error messages for debugging
        # - Include specific words found for transparency
        return FailResult(
            error_message=f"Contains inappropriate words: {', '.join(mentioned_words)}",
            fix_value=None,  # Optional: suggest a corrected version
        )
    else:
        # PassResult: Validation passed
        return PassResult()

print("✓ Custom validator 'toxic-words' created")
print(f"  → Blocks words: {toxic_word_list}")
print(f"  → Validation type: Rule-based (exact word matching)")
print()

# =============================================================================
# PART 2: Combining Custom and Built-in Validators
# =============================================================================

print("=" * 70)
print("COMBINING VALIDATORS: Custom + Built-in")
print("=" * 70)

# Create a guard with BOTH validators:
# 1. ToxicLanguage (built-in): ML-based toxicity detection
#    - threshold=0.8: Lenient (only blocks highly toxic content)
#    - Catches: Hate speech, threats, severe profanity, harassment
# 
# 2. toxic_words (custom): Rule-based word list
#    - Catches: Specific words relevant to our kid-friendly context
#    - Fast and deterministic

print("\nValidator 1: ToxicLanguage (Built-in ML Model)")
print("  → Type: Machine Learning based")
print("  → Threshold: 0.8 (lenient - only severe toxicity)")
print("  → Good for: Complex toxic patterns, context-aware detection")

print("\nValidator 2: toxic_words (Custom Rule-based)")
print("  → Type: Simple word matching")
print("  → Word list: Playground insults")
print("  → Good for: Known bad words, fast execution, kid-friendly content")

print("\n🔍 Why use BOTH?")
print("  • Custom validator: Fast, catches known specific words")
print("  • Built-in validator: Catches complex toxic patterns ML can detect")
print("  • Together: Defense in depth - multiple layers of protection")
print()

guard = Guard().use(
    ToxicLanguage(threshold=0.8, validation_method="sentence", on_fail=OnFailAction.EXCEPTION)
).use(
    toxic_words(on_fail=OnFailAction.EXCEPTION)
)

print("✓ Guard created with 2 validators (must pass BOTH)\n")

# =============================================================================
# PART 3: Testing the Combined Validators
# =============================================================================

print("=" * 70)
print("TESTING: How the validators work together")
print("=" * 70)

test_cases = [
    # (text, should_pass, description, which_catches)
    (
        "Hello! How are you today?",
        True,
        "Completely clean text",
        None
    ),
    (
        "You're such a butt-head!",
        False,
        "Contains playground insult word",
        "Custom (toxic_words)"
    ),
    (
        "This is the most idiotic thing I've ever seen.",
        False,
        "Contains word from our custom list",
        "Custom (toxic_words)"
    ),
    (
        "I will destroy you and everything you love!",
        False,
        "Severe threat - high toxicity score",
        "Built-in (ToxicLanguage)"
    ),
    (
        "That's not very nice, but I understand your frustration.",
        True,
        "Slightly negative but not toxic",
        None
    ),
    (
        "Stop being such a booger-brain, you poop!",
        False,
        "Multiple playground insults",
        "Custom (toxic_words)"
    ),
    (
        "This product is garbage and a waste of money.",
        True,
        "Negative review but not toxic (threshold=0.8 is lenient)",
        None
    ),
]

for i, (text, should_pass, description, which_catches) in enumerate(test_cases, 1):
    print(f"\n{'─' * 70}")
    print(f"Test Case {i}: {description}")
    print(f"{'─' * 70}")
    print(f"Input: '{text}'")
    print(f"Expected: {'✓ PASS' if should_pass else '✗ FAIL'}")
    
    try:
        result = guard.validate(text)
        print(f"Result: ✓ PASSED all validations")
        if not should_pass:
            print(f"⚠ WARNING: Expected this to fail but it passed!")
            print(f"   → May need to adjust threshold or word list")
    except Exception as e:
        print(f"Result: ✗ REJECTED")
        print(f"Reason: {str(e)}")
        if which_catches:
            print(f"Caught by: {which_catches}")
        if should_pass:
            print(f"⚠ WARNING: Expected this to pass but it failed!")