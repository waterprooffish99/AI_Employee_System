<!-- Thank you for opening a pull request! Please follow these guidelines: -->
<!-- 1. Fill out all sections below -->
<!-- 2. Ensure tests pass -->
<!-- 3. Update documentation as needed -->

## Description

<!-- Briefly describe the changes in this PR -->

## Related Issue

<!-- Link to the issue this PR addresses (e.g., Fixes #123) -->
Fixes #

## Type of Change

<!-- Mark the appropriate option with an [x] -->

- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to change)
- [ ] Documentation update
- [ ] Code style update (formatting, renaming)
- [ ] Refactoring (no functional changes)
- [ ] Performance improvement
- [ ] Test addition/update
- [ ] CI/CD update
- [ ] Security fix

## Tier Affected

<!-- Mark all tiers that are affected by this PR -->

- [ ] Bronze 🥉
- [ ] Silver 🥈
- [ ] Gold 🥇
- [ ] Platinum 💎

## Changes Made

<!-- List the specific changes made in this PR -->

1.
2.
3.

## Testing

<!-- Describe the tests you ran to verify your changes -->

- [ ] Bronze Tier tests pass
- [ ] Platinum Demo test passes
- [ ] Manual testing completed
- [ ] New tests added for new functionality

### Test Commands

```bash
# Run Bronze tests
bash test_bronze.sh

# Run Platinum demo test
uv run pytest tests/test_platinum_demo.py -v

# Run specific test
uv run pytest tests/test_*.py::test_name -v
```

## Checklist

<!-- Mark completed items with an [x] -->

- [ ] My code follows the project's style guidelines (PEP 8)
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing tests pass locally with my changes
- [ ] Any dependent changes have been merged and published
- [ ] I have run `scripts/scan_secrets.sh` to ensure no secrets are committed
- [ ] I have updated the CHANGELOG.md (if applicable)

## Screenshots/Recordings

<!-- If applicable, add screenshots or recordings to help explain your changes -->

## Additional Notes

<!-- Add any other context about the PR here -->

## Security

<!-- If this PR involves security changes, please describe them below -->

- [ ] No credentials or secrets added
- [ ] No sensitive data logged
- [ ] Input validation added (if applicable)
- [ ] Security implications considered

---

**By submitting this pull request, I confirm that:**
- I have read and agree to the [Contributing Guidelines](CONTRIBUTING.md)
- I have followed the [Code of Conduct](CODE_OF_CONDUCT.md)
- My contribution is my own original work
- I grant the project the right to use my contribution
