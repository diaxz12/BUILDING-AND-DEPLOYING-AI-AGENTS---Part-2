# Use multiple guardrails from the hub: https://hub.guardrailsai.com/
from guardrails import Guard, OnFailAction
from guardrails.hub import CompetitorCheck, ToxicLanguage

"""
GUARDRAILS EXAMPLE: Combining Multiple Validators

This example demonstrates how to use multiple guardrails together to
enforce multiple safety and business rules simultaneously.

USE CASE:
We're building a customer service chatbot for a tech company that needs to:
1. Avoid mentioning competitor companies (brand protection)
2. Prevent toxic/offensive language (customer experience)

WHY THIS MATTERS:
- Brand Protection: Prevents your AI from promoting competitors
- User Safety: Keeps conversations respectful and professional
- Business Compliance: Maintains brand guidelines and community standards
- Reputation Management: Protects company image in customer interactions
"""

# =============================================================================
# SETUP: Configure Multiple Guardrails
# =============================================================================

print("=" * 70)
print("SETTING UP GUARDRAILS")
print("=" * 70)

# GUARDRAIL 1: CompetitorCheck
# - Detects mentions of competitor company names
# - Case-insensitive matching
# - Useful for: Marketing content, chatbot responses, product descriptions
competitor_list = ["Apple", "Microsoft", "Google"]
print(f"✓ CompetitorCheck: Blocking mentions of {competitor_list}")

# GUARDRAIL 2: ToxicLanguage
# - Detects offensive, rude, or harmful language
# - threshold=0.5: Toxicity score from 0 (safe) to 1 (very toxic)
#   → 0.5 means moderately strict (blocks medium-to-high toxicity)
# - validation_method="sentence": Checks each sentence individually
#   → Alternative: "full" checks entire text as one block
print(f"✓ ToxicLanguage: Threshold=0.5 (moderately strict)")
print(f"  → Validation method: sentence-by-sentence analysis")
print()

# CREATE THE GUARD with multiple validators
# use_many() applies ALL validators - text must pass ALL checks
guard = Guard().use_many(
    CompetitorCheck(
        competitors=competitor_list,
        on_fail=OnFailAction.EXCEPTION
    ),
    ToxicLanguage(
        threshold=0.5,
        validation_method="sentence",
        on_fail=OnFailAction.EXCEPTION
    )
)

print("✓ Guard created with 2 validators (must pass BOTH)\n")

# =============================================================================
# TEST 1: Safe Text (No Competitors, No Toxicity)
# =============================================================================

print("=" * 70)
print("TEST 1: Safe, neutral text")
print("=" * 70)

safe_text = """An apple a day keeps a doctor away.
This is good advice for keeping your health."""

print(f"Input text:\n  '{safe_text}'\n")

try:
    result = guard.validate(safe_text)
    print("✓ SUCCESS: Text passed all validations")
    print("  ✓ CompetitorCheck: No competitor mentions detected")
    print("     → 'apple' (lowercase, fruit context) ≠ 'Apple' (company)")
    print("  ✓ ToxicLanguage: No toxic language detected")
    print("  → This text is safe to use!\n")
except Exception as e:
    print(f"✗ FAILED: {e}\n")

# =============================================================================
# TEST 2: Problematic Text (Has Competitors AND Toxicity)
# =============================================================================

print("=" * 70)
print("TEST 2: Text with multiple violations")
print("=" * 70)

problematic_text = """Shut the hell up! Apple just released a new iPhone."""

print(f"Input text:\n  '{problematic_text}'\n")

try:
    result = guard.validate(problematic_text)
    print("✓ Text passed (this shouldn't happen!)\n")
except Exception as e:
    print("✗ REJECTED: Text violated guardrail policies")
    print(f"\n  Validation Error Details:")
    print(f"  {e}")
    print("\n  Why this was blocked:")
    print("  ✗ CompetitorCheck: Mentions 'Apple' (competitor company)")
    print("  ✗ ToxicLanguage: Contains aggressive language ('Shut the hell up')")
    print("  → Text must pass ALL validators - this failed BOTH\n")

# =============================================================================
# TEST 3: Edge Cases - Understanding Each Validator
# =============================================================================

print("=" * 70)
print("TEST 3: Edge cases to understand validator behavior")
print("=" * 70)

test_cases = [
    # (text, expected_result, description, which_fails)
    (
        "I love eating apples and oranges!",
        "PASS",
        "Lowercase 'apples' (fruit) - should pass",
        None
    ),
    (
        "Apple Inc. is mentioned in this sentence.",
        "FAIL",
        "Explicit company mention",
        "CompetitorCheck"
    ),
    (
        "This is absolutely terrible and frustrating!",
        "FAIL",
        "Strong negative language (high toxicity score)",
        "ToxicLanguage"
    ),
    (
        "I disagree with this approach.",
        "PASS",
        "Polite disagreement - not toxic",
        None
    ),
    (
        "Check out Microsoft's new features, they're amazing!",
        "FAIL",
        "Competitor mention (even if positive)",
        "CompetitorCheck"
    ),
    (
        "You're an idiot! Google has better search results.",
        "FAIL",
        "Both toxic language AND competitor mention",
        "Both"
    ),
]

for i, (text, expected, description, fails) in enumerate(test_cases, 1):
    print(f"\nTest Case {i}: {description}")
    print(f"Text: '{text}'")
    
    try:
        guard.validate(text)
        print(f"  Result: ✓ PASSED")
        if expected == "FAIL":
            print(f"  ⚠ WARNING: Expected to fail but passed!")
    except Exception as e:
        print(f"  Result: ✗ REJECTED")
        if fails:
            print(f"  Failed validator(s): {fails}")
        if expected == "PASS":
            print(f"  ⚠ WARNING: Expected to pass but failed!")