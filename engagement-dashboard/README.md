# ⚡ X Engagement Dashboard

**Pre-evaluate your tweets before posting using X's open-sourced algorithm!**

This tool analyzes tweet content to predict engagement potential and identifies issues that could cause your tweet to be buried, downranked, or filtered. Based on comprehensive analysis of X's (formerly Twitter) [open-sourced recommendation algorithm](https://github.com/twitter/the-algorithm).

## 🎯 What It Does

The Engagement Dashboard evaluates tweets on factors that can be analyzed **before posting**:

- **Safety Signals**: Detects toxicity, spam, NSFW content, and suspicious URLs that trigger filters
- **Quality Metrics**: Analyzes text length, capitalization, formatting, and structural quality
- **Engagement Boosters**: Identifies features that increase engagement (questions, media, optimal length)
- **Penalty Detection**: Flags issues that cause immediate burial or downranking
- **Recommendations**: Provides actionable tips to improve tweet performance

## 🚀 Quick Start

### Web Interface (Easiest)

1. Open `index.html` in your web browser
2. Type or paste your tweet
3. Select media options if applicable
4. Click "Analyze Tweet"
5. Review your score and recommendations!

### Python CLI

```bash
# Interactive mode
python3 analyzer.py

# Analyze specific text
python3 analyzer.py "Your tweet text here"
```

## 📊 Scoring System

### Overall Score: 0-100

- **80-100**: Low Risk - Great engagement potential
- **60-79**: Medium Risk - Decent performance expected
- **40-59**: High Risk - May have limited visibility
- **0-39**: Critical Risk - Likely to be buried or filtered

### Component Scores

1. **Safety Score (40% weight)** - Most critical
   - Toxicity detection
   - Spam pattern detection
   - NSFW content detection
   - URL trustworthiness

2. **Quality Score (30% weight)**
   - Text length optimization
   - Capitalization ratio
   - Formatting quality
   - Hashtag usage

3. **Engagement Score (30% weight)**
   - Question presence
   - Media attachments
   - Optimal length range
   - Clean formatting

## 🔍 What Gets Analyzed

### Pre-Posting Evaluable Features

Based on X's algorithm source code analysis, the tool evaluates:

#### Text Features
- **Length**: Character count (optimal: 100-200 chars)
- **Capitalization**: Ratio of uppercase letters (max 30%)
- **Questions**: Presence of "?" (boosts replies)
- **Whitespace**: Newlines and spacing
- **Formatting**: Overall text structure

#### Content Features
- **URLs**: Count and domain trustworthiness
- **Mentions**: @username count
- **Hashtags**: # count (optimal: 1-3, max: 5)
- **Media**: Presence and type (video > image > gif)

#### Safety Features
- **Toxic Language**: Hate speech, insults, threats
- **Spam Indicators**: "Click here", "buy now", "follow for follow"
- **NSFW Content**: Sexual or explicit language
- **Suspicious URLs**: Shortened links, untrusted domains

## ⚠️ Critical Penalties (Can Bury Your Tweet)

### Hard Filters (Complete Removal)
These trigger automatic filtering by Grok ML models:
- **GrokSpamFilter**: Spam content detected
- **GrokNsfwFilter**: NSFW content detected
- **GrokViolentFilter**: Violent content detected
- **GrokGoreFilter**: Graphic violence detected

### Severe Downranking
These move tweets to "Abusive Quality" section (bottom of thread):
- **High Toxicity Score**: Toxic language
- **High Spammy Content Score**: Spam patterns
- **Untrusted URL**: Suspicious/shortened links
- **Downrank Spam Reply**: Spam reply detection

### Multiplicative Penalties
These reduce your score by percentage:
- **Out-of-Network (OON) Penalty**: 0.75x multiplier (25% reduction)
  - Applied to tweets from accounts users don't follow
  - Simulated in the tool as 15% reduction
- **Feedback Fatigue**: 0.2x-1.0x multiplier
  - Based on "See Fewer" user feedback
  - Cannot be predicted pre-posting (requires user history)

## ✅ Engagement Boosters

### Major Boosts (+20-30%)
- **Video Content**: +30% engagement
- **Image Content**: +25% engagement
- **GIF Content**: +20% engagement

### Moderate Boosts (+10-15%)
- **Questions**: +15% (increases replies)
- **Optimal Length**: +10% (100-200 chars)

### Minor Boosts (+5%)
- **Clean Formatting**: +5% (proper capitalization)

## 📖 Examples

### Example 1: High Risk Tweet

**Input:**
```
CLICK HERE NOW!!! 🚨 BUY BITCOIN AND MAKE $10,000 FAST!!! 💰💰💰
LIMITED TIME OFFER!!! DM ME NOW!!! bit.ly/scam123
```

**Analysis:**
- Overall Score: 12/100 - CRITICAL RISK
- Safety Score: 10/100
- Penalties:
  - HIGH_SPAMMY_CONTENT: -70% (spam patterns)
  - UNTRUSTED_URL: -40% (suspicious link)
  - EXCESSIVE_CAPS: -40% (90% caps ratio)

**Verdict**: Will likely be filtered by GrokSpamFilter ❌

---

### Example 2: Low Risk Tweet

**Input:**
```
Just finished reading an amazing article about machine learning ethics. The intersection of AI safety and practical deployment is fascinating. What are your thoughts on responsible AI development? 🤔

[Has image attachment]
```

**Analysis:**
- Overall Score: 89/100 - LOW RISK
- Safety Score: 100/100
- Quality Score: 95/100
- Engagement Score: 90/100
- Boosts:
  - IMAGE_MEDIA: +25%
  - HAS_QUESTION: +15%
  - OPTIMAL_LENGTH: +10%
  - GOOD_FORMATTING: +5%

**Verdict**: Excellent engagement potential! ✅

---

### Example 3: Medium Risk Tweet

**Input:**
```
This is the WORST product I've ever used. Complete garbage. The developers are idiots who don't know what they're doing.
```

**Analysis:**
- Overall Score: 42/100 - HIGH RISK
- Safety Score: 55/100
- Penalties:
  - HIGH_TOXICITY: -45% (toxic language: "worst", "garbage", "idiots")
- Warnings:
  - May be downranked to "Abusive Quality" section

**Verdict**: High risk of downranking ⚠️

---

### Example 4: Optimized Tweet

**Input:**
```
Working on a new feature for our app that lets users customize their dashboard. Here's a sneak peek of the design! What features would you like to see added? 👀

[Has video attachment]
```

**Analysis:**
- Overall Score: 92/100 - LOW RISK
- Safety Score: 100/100
- Quality Score: 100/100
- Engagement Score: 95/100
- Boosts:
  - VIDEO_MEDIA: +30%
  - HAS_QUESTION: +15%
  - OPTIMAL_LENGTH: +10%
  - GOOD_FORMATTING: +5%

**Verdict**: Perfect! Maximum engagement potential! ✅

## 🎓 Algorithm Insights

### Based on X's Open-Sourced Code

The tool is built on analysis of these key components:

1. **Home Mixer** (`home-mixer/`): Timeline ranking and scoring
   - `HomeFeatures.scala`: 100+ tweet features
   - `PhoenixScorer.scala`: ML-based engagement prediction
   - `OONTweetScalingScorer.scala`: Out-of-network penalty (0.75x)
   - `FeedbackFatigueScorer.scala`: "See Fewer" penalty system

2. **Visibility Lib** (`visibilitylib/`): Content filtering and safety
   - `DownrankingRules.scala`: Safety-based downranking logic
   - Grok ML model filters (spam, NSFW, toxicity, violence)
   - Safety label thresholds and penalties

3. **Trust & Safety Models** (`trust_and_safety_models/`):
   - pNSFWMedia: NSFW image detection
   - pNSFWText: NSFW text detection
   - pToxicity: Toxicity detection
   - pAbuse: Abuse/hate speech detection

### Key Algorithm Findings

1. **Safety is Paramount**: Safety penalties can cause complete burial
2. **Out-of-Network Penalty**: 25% reduction for accounts you don't follow
3. **Media Matters**: Video content gets 30% engagement boost
4. **Questions Work**: Adding "?" increases reply likelihood
5. **Length Optimization**: 100-200 characters is the sweet spot
6. **Caps Lock = Spam**: High capitalization triggers spam detection
7. **Hashtag Moderation**: More than 5 hashtags reduces engagement

## 🔧 Technical Details

### Python Analyzer (`analyzer.py`)

- Pure Python 3 implementation
- No external dependencies required
- Comprehensive pattern matching for safety detection
- Feature extraction and scoring algorithms
- JSON export capability

### Web Interface (`index.html`)

- Single-file HTML/CSS/JavaScript
- No server required - runs entirely in browser
- JavaScript port of Python analyzer
- Real-time analysis and visualization
- Responsive design

## 📝 Recommendations

### For Maximum Engagement

1. ✅ **Add media** (especially video)
2. ✅ **Ask questions** to encourage replies
3. ✅ **Keep it 100-200 characters** (sweet spot)
4. ✅ **Use 1-3 relevant hashtags** (not more)
5. ✅ **Use sentence case** (avoid all caps)
6. ✅ **Include direct links** (avoid URL shorteners)

### To Avoid Burial

1. ❌ **No toxic language** (hate, insults, threats)
2. ❌ **No spam patterns** ("click here", "buy now", "f4f")
3. ❌ **No NSFW content** (explicit language/topics)
4. ❌ **No suspicious URLs** (shortened links, untrusted domains)
5. ❌ **No excessive caps** (keep below 30%)
6. ❌ **No hashtag spam** (max 5, ideally 1-3)

## ⚖️ Limitations

This tool analyzes **pre-posting factors only**. It cannot predict:

- **Engagement metrics**: Actual likes, retweets, replies (requires post data)
- **Author authority**: Follower count, verification status, reputation
- **User-specific signals**: Your relationship with followers
- **Timing factors**: When you post, recency effects
- **Topic relevance**: Interest matching with followers
- **Feedback fatigue**: Historical "See Fewer" feedback

The tool provides a **baseline assessment** focused on content quality and safety signals that can cause immediate penalties.

## 📚 Further Reading

- [X's Algorithm Repository](https://github.com/twitter/the-algorithm)
- [Home Mixer Documentation](https://github.com/twitter/the-algorithm/tree/main/home-mixer)
- [Visibility Library](https://github.com/twitter/the-algorithm/tree/main/visibilitylib)
- [Trust & Safety Models](https://github.com/twitter/the-algorithm/tree/main/trust_and_safety_models)
- [Algorithm Explanation (README)](https://github.com/twitter/the-algorithm/blob/main/README.md)

## 🎮 Try It Out!

### Good Tweet Examples to Test

```
# High engagement potential
"Just discovered this amazing productivity hack that saves me 2 hours a day. The secret? Batching similar tasks together. What's your favorite productivity tip? 🚀 [+ image]"

# Question engagement
"Quick poll: Do you prefer tabs or spaces for code indentation? (This is a safe space... mostly) 😄"

# Media boost with context
"Behind the scenes of our new product launch! Here's what went into building this feature 👇 [+ video]"
```

### Bad Tweet Examples to Test

```
# Spam (will fail)
"CLICK HERE NOW!!! Make $5000 working from home!!! Limited time offer!!! bit.ly/123"

# Toxicity (will fail)
"This company is absolute garbage run by complete idiots. Worst service ever."

# NSFW (will fail)
"Check out my adult content on [explicit site]. Click link in bio for more xxx content."
```

## 🤝 Contributing

This is an educational tool based on X's open-sourced algorithm. Suggestions and improvements welcome!

## 📄 License

Educational and entertainment purposes. Based on publicly available algorithm source code from X (Twitter).

## 🙏 Acknowledgments

Built from analysis of X's open-sourced recommendation algorithm:
- https://github.com/twitter/the-algorithm

Special thanks to X for open-sourcing their algorithm and enabling this kind of educational analysis!

---

**Have fun optimizing your tweets! 🚀**
