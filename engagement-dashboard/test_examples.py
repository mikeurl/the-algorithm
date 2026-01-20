#!/usr/bin/env python3
"""
Test Examples for X Engagement Dashboard

Run this to see how different tweet types are scored.
"""

from analyzer import EngagementAnalyzer, format_analysis_report


def print_separator():
    print('\n' + '=' * 80 + '\n')


def test_tweet(description, text, has_media=False, media_type=None, is_reply=False):
    """Test a single tweet and print results"""
    print(f"TEST: {description}")
    print_separator()
    print(f"TWEET TEXT:\n{text}")
    print_separator()

    analyzer = EngagementAnalyzer()
    result = analyzer.analyze(text, has_media, media_type, is_reply)

    print(format_analysis_report(result))
    print_separator()
    input("Press Enter to continue to next example...")
    print_separator()


def run_all_tests():
    """Run all test examples"""
    print("=" * 80)
    print("X ENGAGEMENT DASHBOARD - TEST EXAMPLES")
    print("=" * 80)
    print("\nRunning various tweet examples to demonstrate the analyzer...")
    print_separator()

    # Example 1: SPAM - Should fail badly
    test_tweet(
        "SPAM TWEET - Should Score Poorly",
        "🚨 CLICK HERE NOW!!! 💰 MAKE $10,000 WORKING FROM HOME!!! 💰\n"
        "LIMITED TIME OFFER!!! BUY BITCOIN AND GET RICH FAST!!!\n"
        "DM FOR MORE INFO!!! Follow for follow!!! F4F L4L!!!\n"
        "bit.ly/totally-not-a-scam 🤑🤑🤑",
        has_media=False
    )

    # Example 2: TOXIC - Should get safety penalties
    test_tweet(
        "TOXIC TWEET - Should Trigger Safety Penalties",
        "This is the WORST app I've ever used. The developers are complete idiots. "
        "Such garbage. Everyone who uses this is stupid. I hate this trash.",
        has_media=False
    )

    # Example 3: NSFW - Should get filtered
    test_tweet(
        "NSFW TWEET - Should Trigger Content Filter",
        "Check out my explicit adult content! Link to porn site in bio. "
        "18+ only, very sexual content, nude photos available. XXX content here!",
        has_media=False
    )

    # Example 4: EXCESSIVE CAPS - Quality penalty
    test_tweet(
        "ALL CAPS TWEET - Should Get Quality Penalty",
        "THIS IS MY TWEET AND I'M SHOUTING BECAUSE I WANT ATTENTION!!! "
        "EVERYTHING IS IN CAPS!!! LOOK AT ME!!!",
        has_media=False
    )

    # Example 5: TOO MANY HASHTAGS - Engagement penalty
    test_tweet(
        "HASHTAG SPAM - Should Reduce Engagement",
        "Just posted a new photo! #photography #nature #beautiful #amazing #instagood "
        "#photooftheday #picoftheday #love #follow #like #instadaily #art #happy",
        has_media=True,
        media_type="image"
    )

    # Example 6: TOO SHORT - Low engagement
    test_tweet(
        "TOO SHORT - Low Engagement Expected",
        "ok",
        has_media=False
    )

    # Example 7: OPTIMAL TWEET - Should score well
    test_tweet(
        "OPTIMAL TWEET - Should Score High",
        "Just finished reading an amazing article about the future of AI and machine learning. "
        "The intersection of ethics and practical deployment is fascinating. "
        "What are your thoughts on responsible AI development? 🤔",
        has_media=True,
        media_type="image"
    )

    # Example 8: PERFECT WITH VIDEO - Should score highest
    test_tweet(
        "PERFECT TWEET WITH VIDEO - Maximum Score",
        "Behind the scenes of building our new feature! Here's a quick walkthrough of the "
        "development process and the challenges we faced. What features would you like to see next? 🚀",
        has_media=True,
        media_type="video"
    )

    # Example 9: GOOD QUESTION TWEET - Engagement boost
    test_tweet(
        "QUESTION TWEET - Should Boost Replies",
        "Quick question for developers: When writing tests, do you prefer TDD (test-driven development) "
        "or writing tests after implementation? I'm curious about different workflows! 🤔",
        has_media=False
    )

    # Example 10: TECHNICAL TWEET WITH IMAGE - Good balance
    test_tweet(
        "TECHNICAL CONTENT WITH MEDIA - Well Balanced",
        "Finally solved that tricky bug in our async processing pipeline! Turns out the race condition "
        "was caused by improper lock handling. Here's the fix 👇",
        has_media=True,
        media_type="image"
    )

    # Example 11: SUSPICIOUS URL - Should trigger warning
    test_tweet(
        "SUSPICIOUS URL - Should Trigger Warning",
        "Check out this amazing deal! Click here for more info: bit.ly/123abc "
        "Limited time only! Visit: tinyurl.com/xyz789",
        has_media=False
    )

    # Example 12: CLEAN ANNOUNCEMENT - Should do well
    test_tweet(
        "CLEAN ANNOUNCEMENT - Good Engagement Potential",
        "Excited to announce that we're launching our new product next week! "
        "It's been months of hard work and we can't wait to share it with you. "
        "Stay tuned for the big reveal! 🎉",
        has_media=True,
        media_type="gif"
    )

    # Example 13: THREAD STARTER - Good for replies
    test_tweet(
        "THREAD STARTER - Designed for Engagement",
        "Let me share 5 productivity tips that changed how I work:\n\n"
        "1. Time blocking - dedicating specific hours to specific tasks\n"
        "2. Batch processing - handling similar tasks together\n"
        "3. The 2-minute rule - if it takes less than 2 minutes, do it now\n\n"
        "Which one do you use? 🧵",
        has_media=False
    )

    # Example 14: MODERATE LENGTH NO MEDIA - Baseline
    test_tweet(
        "MODERATE TWEET WITHOUT MEDIA - Baseline Score",
        "Working on improving our documentation today. Good docs are just as important "
        "as good code, but they're often overlooked. Taking the time to write clear, "
        "helpful documentation pays dividends in the long run.",
        has_media=False
    )

    # Example 15: BORDERLINE TOXIC - Edge case
    test_tweet(
        "BORDERLINE NEGATIVE - Edge Case Testing",
        "Really disappointed with this update. The new UI is confusing and removes features "
        "that I used daily. I understand change is necessary, but this feels like a step backwards. "
        "Hope they reconsider some of these decisions.",
        has_media=False
    )

    print("\n" + "=" * 80)
    print("ALL TESTS COMPLETE!")
    print("=" * 80)
    print("\nKey Takeaways:")
    print("1. Spam and toxic content gets heavily penalized")
    print("2. Media (especially video) provides significant engagement boost")
    print("3. Questions increase reply likelihood")
    print("4. Optimal length is 100-200 characters")
    print("5. Excessive caps, hashtags, and suspicious URLs hurt performance")
    print("6. Clean, well-formatted content with context performs best")
    print("=" * 80)


if __name__ == '__main__':
    import sys

    print("\nX Engagement Dashboard - Test Examples")
    print("This will run through 15 example tweets to demonstrate the analyzer.\n")

    response = input("Ready to start? (y/n): ")
    if response.lower().startswith('y'):
        run_all_tests()
    else:
        print("Cancelled.")
