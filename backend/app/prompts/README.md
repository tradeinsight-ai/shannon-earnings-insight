# Prompts Directory

This directory contains prompts used by various AI analysis services in the EarningsInsight application.

## File Organization

- `earnings_analysis_prompt.md` - Main prompt for analyzing earnings call transcripts
- Future: Additional prompts for specialized analysis tasks

## Usage

These prompts are loaded by the AI analysis service at runtime. To update analysis behavior:

1. Edit the relevant prompt file
2. Test with sample transcripts
3. Deploy updated prompt with the application

## Best Practices

- Keep prompts clear and specific
- Include output format specifications
- Provide examples when helpful
- Version control prompt changes
- Document prompt updates in commit messages

## Prompt Development

When creating or modifying prompts:

1. **Test thoroughly** - Use a variety of transcript types
2. **Iterate** - Refine based on output quality
3. **Document changes** - Explain why prompts were modified
4. **Consider edge cases** - Handle transcripts with unusual content
5. **Maintain consistency** - Keep output format stable for frontend compatibility
