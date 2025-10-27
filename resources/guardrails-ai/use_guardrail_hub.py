# Use one of the guardrails available on the hub: https://hub.guardrailsai.com/
from guardrails import Guard, OnFailAction
from guardrails.hub import RegexMatch

"""
GUARDRAILS EXAMPLE: Detecting and Rejecting Phone Numbers

This example demonstrates how to use Guardrails AI to protect against
sensitive information (PII - Personally Identifiable Information) being
included in user input or LLM outputs.

USE CASE: 
We want to reject any text that contains Portuguese phone numbers
and allow normal text to pass through.

WHY THIS MATTERS:
- Prevents accidental sharing of personal phone numbers
- Protects user privacy
- Ensures compliance with data protection regulations (GDPR, etc.)
"""

# REGEX PATTERN EXPLANATION:
# ^                     - Start of string
# (?!.*(...))          - Negative lookahead: fails if pattern is found anywhere
# \+?351               - Optional + sign followed by Portugal country code (351)
# [ -]?                - Optional space or hyphen separator
# \d{2,3}              - 2-3 digits (area code)
# [ -]?                - Optional space or hyphen
# \d{3}                - 3 digits
# [ -]?                - Optional space or hyphen
# \d{3,4}              - 3-4 digits (last part of phone number)
# .*$                  - Match rest of string

portuguese_phone_pattern = r"^(?!.*(\+?351[ -]?\d{2,3}[ -]?\d{3}[ -]?\d{3,4})).*$"

# CREATE THE GUARD:
# - RegexMatch: Validates that input matches the regex pattern
# - on_fail=EXCEPTION: Raises an error if validation fails
guard = Guard().use(
    RegexMatch, 
    regex=portuguese_phone_pattern,
    on_fail=OnFailAction.EXCEPTION 
)

# TEST 1: Normal text (should PASS - no phone number detected)
print("=" * 60)
print("TEST 1: Normal text without phone numbers")
print("=" * 60)
try:
    result = guard.validate("Hello world!")
    print("✓ SUCCESS: 'Hello world!' passed validation")
    print("  → No phone number detected, text is safe\n")
except Exception as e:
    print(f"✗ FAILED: {e}\n")

# TEST 2: Text with Portuguese phone number (should FAIL - phone number detected)
print("=" * 60)
print("TEST 2: Text containing a Portuguese phone number")
print("=" * 60)
try:
    result = guard.validate("+351 911 234 567")
    print("✓ Phone number passed (this shouldn't happen!)")
except Exception as e:
    print("✗ REJECTED: Phone number detected and blocked")
    print(f"  → Reason: Contains Portuguese phone number")
    print(f"  → This protects user privacy!\n")

# TEST 3: More examples
print("=" * 60)
print("TEST 3: Additional test cases")
print("=" * 60)

test_cases = [
    ("My email is user@example.com", True, "Email (non-phone PII)"),
    ("Call me at 351911234567", False, "Phone number without formatting"),
    ("The meeting is at 3pm tomorrow", True, "Normal sentence with numbers"),
    ("Contact: +351-21-123-4567", False, "Lisbon landline with formatting"),
]

for text, should_pass, description in test_cases:
    try:
        guard.validate(text)
        status = "✓ PASSED" if should_pass else "⚠ PASSED (unexpected)"
        print(f"{status}: {description}")
        print(f"   Text: '{text}'")
    except Exception as e:
        status = "✗ REJECTED" if not should_pass else "⚠ REJECTED (unexpected)"
        print(f"{status}: {description}")
        print(f"   Text: '{text}'")
    print()