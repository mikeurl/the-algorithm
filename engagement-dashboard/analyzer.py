#!/usr/bin/env python3
"""
X Engagement Dashboard - Pre-Posting Tweet Analyzer

This tool evaluates tweets/comments before posting based on X's open-sourced
engagement algorithms. It focuses on factors that can be evaluated pre-posting
and identifies issues that could "bury" your post immediately.

Based on analysis of: https://github.com/twitter/the-algorithm
"""

import re
import json
from typing import Dict, List, Tuple
from dataclasses import dataclass, asdict
from urllib.parse import urlparse


@dataclass
class AnalysisResult:
    """Complete analysis result for a tweet"""
    overall_score: float  # 0-100
    risk_level: str  # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    safety_score: float
    quality_score: float
    engagement_potential: float
    penalties: List[Dict[str, any]]
    boosts: List[Dict[str, any]]
    warnings: List[str]
    recommendations: List[str]
    feature_breakdown: Dict[str, any]


class EngagementAnalyzer:
    """Analyzes tweet content for engagement potential"""

    # Toxicity patterns (simplified - real model uses ML)
    TOXIC_PATTERNS = [
        r'\b(hate|stupid|idiot|dumb|trash|garbage|worst)\b',
        r'\b(kill|die|death|hurt)\s+(you|yourself|them)',
        r'\b(f\*ck|sh\*t|damn|hell)\s+(you|off)',
        r'\b(loser|pathetic|disgusting|horrible)\b',
    ]

    # Spam indicators
    SPAM_PATTERNS = [
        r'(?i)(click here|follow for follow|f4f|l4l)',
        r'(?i)(buy now|limited time|act now|offer expires)',
        r'(?i)(make \$\d+|earn money fast|work from home)',
        r'(?i)(crypto|bitcoin|nft).*(guaranteed|profit|returns)',
        r'(?i)(dm for|check bio|link in bio).*(\$|money|cash|paid)',
    ]

    # NSFW text patterns
    NSFW_PATTERNS = [
        r'(?i)\b(sex|porn|xxx|nsfw|nude|naked)\b',
        r'(?i)\b(sexual|explicit|adult content)\b',
    ]

    # Untrusted URL patterns (common spam/malicious domains)
    SUSPICIOUS_DOMAINS = [
        'bit.ly', 'tinyurl.com', 'shorturl.at',  # Shortened URLs are suspicious
        'click', 'offer', 'promo', 'deals',  # Common in spam
    ]

    # Optimal ranges based on algorithm analysis
    OPTIMAL_LENGTH_MIN = 50
    OPTIMAL_LENGTH_MAX = 280
    SWEET_SPOT_MIN = 100
    SWEET_SPOT_MAX = 200

    MAX_CAPS_RATIO = 0.3  # More than 30% caps is bad
    RECOMMENDED_CAPS_RATIO = 0.1  # 10% is okay

    def __init__(self):
        self.toxic_regex = [re.compile(p, re.IGNORECASE) for p in self.TOXIC_PATTERNS]
        self.spam_regex = [re.compile(p, re.IGNORECASE) for p in self.SPAM_PATTERNS]
        self.nsfw_regex = [re.compile(p, re.IGNORECASE) for p in self.NSFW_PATTERNS]

    def analyze(self, text: str, has_media: bool = False,
                media_type: str = None, is_reply: bool = False) -> AnalysisResult:
        """
        Analyze tweet for engagement potential

        Args:
            text: Tweet text content
            has_media: Whether tweet has media attachments
            media_type: Type of media (image, video, gif)
            is_reply: Whether this is a reply
        """
        # Extract features
        features = self._extract_features(text, has_media, media_type, is_reply)

        # Safety analysis (MOST CRITICAL - can cause immediate burial)
        safety_score, safety_warnings, safety_penalties = self._analyze_safety(text, features)

        # Quality analysis
        quality_score, quality_warnings, quality_penalties = self._analyze_quality(features)

        # Engagement potential
        engagement_score, engagement_boosts = self._analyze_engagement_potential(features)

        # Calculate overall score
        overall_score = self._calculate_overall_score(
            safety_score, quality_score, engagement_score, features
        )

        # Determine risk level
        risk_level = self._determine_risk_level(overall_score, safety_score, safety_penalties)

        # Combine all warnings and recommendations
        all_warnings = safety_warnings + quality_warnings
        recommendations = self._generate_recommendations(
            features, safety_score, quality_score, engagement_score, safety_penalties, quality_penalties
        )

        all_penalties = safety_penalties + quality_penalties

        return AnalysisResult(
            overall_score=round(overall_score, 1),
            risk_level=risk_level,
            safety_score=round(safety_score, 1),
            quality_score=round(quality_score, 1),
            engagement_potential=round(engagement_score, 1),
            penalties=all_penalties,
            boosts=engagement_boosts,
            warnings=all_warnings,
            recommendations=recommendations,
            feature_breakdown=features
        )

    def _extract_features(self, text: str, has_media: bool,
                         media_type: str, is_reply: bool) -> Dict:
        """Extract all analyzable features from tweet"""
        # Basic text features
        text_length = len(text)
        char_count = len([c for c in text if not c.isspace()])

        # Capitalization analysis
        upper_count = sum(1 for c in text if c.isupper())
        caps_ratio = upper_count / char_count if char_count > 0 else 0

        # Whitespace analysis
        whitespace_count = sum(1 for c in text if c.isspace())
        newline_count = text.count('\n')

        # Question detection (engagement boost)
        question_marks = text.count('?')
        has_question = '?' in text

        # URL extraction
        url_pattern = r'https?://[^\s]+'
        urls = re.findall(url_pattern, text)
        url_count = len(urls)

        # Mention detection
        mention_pattern = r'@\w+'
        mentions = re.findall(mention_pattern, text)
        mention_count = len(mentions)

        # Hashtag detection
        hashtag_pattern = r'#\w+'
        hashtags = re.findall(hashtag_pattern, text)
        hashtag_count = len(hashtags)

        # Check for suspicious URLs
        suspicious_urls = []
        for url in urls:
            try:
                domain = urlparse(url).netloc.lower()
                if any(suspicious in domain for suspicious in self.SUSPICIOUS_DOMAINS):
                    suspicious_urls.append(url)
            except:
                suspicious_urls.append(url)  # Malformed URLs are suspicious

        return {
            'text_length': text_length,
            'char_count': char_count,
            'caps_ratio': caps_ratio,
            'upper_count': upper_count,
            'whitespace_count': whitespace_count,
            'newline_count': newline_count,
            'has_question': has_question,
            'question_count': question_marks,
            'urls': urls,
            'url_count': url_count,
            'suspicious_urls': suspicious_urls,
            'mentions': mentions,
            'mention_count': mention_count,
            'hashtags': hashtags,
            'hashtag_count': hashtag_count,
            'has_media': has_media,
            'media_type': media_type,
            'is_reply': is_reply,
        }

    def _analyze_safety(self, text: str, features: Dict) -> Tuple[float, List[str], List[Dict]]:
        """
        Analyze safety signals - CRITICAL for avoiding burial
        Returns: (score, warnings, penalties)
        """
        score = 100.0
        warnings = []
        penalties = []

        # Check toxicity patterns
        toxic_matches = []
        for pattern in self.toxic_regex:
            matches = pattern.findall(text)
            if matches:
                toxic_matches.extend(matches)

        if toxic_matches:
            penalty_severity = min(len(toxic_matches) * 15, 60)
            score -= penalty_severity
            penalties.append({
                'type': 'HIGH_TOXICITY',
                'severity': 'CRITICAL' if penalty_severity > 40 else 'HIGH',
                'impact': f'-{penalty_severity}%',
                'description': f'Toxic language detected: {len(toxic_matches)} pattern(s)',
                'details': f'Matched: {", ".join(set(toxic_matches[:3]))}...'
            })
            warnings.append(f'🚨 CRITICAL: Toxic language detected - may be filtered or downranked to "Abusive Quality" section')

        # Check spam patterns
        spam_matches = []
        for pattern in self.spam_regex:
            matches = pattern.findall(text)
            if matches:
                spam_matches.extend(matches)

        if spam_matches:
            penalty_severity = min(len(spam_matches) * 20, 70)
            score -= penalty_severity
            penalties.append({
                'type': 'HIGH_SPAMMY_CONTENT',
                'severity': 'CRITICAL' if penalty_severity > 50 else 'HIGH',
                'impact': f'-{penalty_severity}%',
                'description': f'Spam patterns detected: {len(spam_matches)} indicator(s)',
                'details': f'Matched: {", ".join(set([m[0] if isinstance(m, tuple) else m for m in spam_matches[:3]]))}...'
            })
            warnings.append(f'🚨 CRITICAL: Spam indicators detected - may trigger GrokSpamFilter (hard filter)')

        # Check NSFW patterns
        nsfw_matches = []
        for pattern in self.nsfw_regex:
            matches = pattern.findall(text)
            if matches:
                nsfw_matches.extend(matches)

        if nsfw_matches:
            penalty_severity = 50
            score -= penalty_severity
            penalties.append({
                'type': 'NSFW_CONTENT',
                'severity': 'CRITICAL',
                'impact': f'-{penalty_severity}%',
                'description': 'NSFW content detected',
                'details': f'Matched: {", ".join(set(nsfw_matches[:3]))}...'
            })
            warnings.append(f'🚨 CRITICAL: NSFW content detected - may trigger GrokNsfwFilter (hard filter)')

        # Check suspicious URLs
        if features['suspicious_urls']:
            penalty_severity = 40
            score -= penalty_severity
            penalties.append({
                'type': 'UNTRUSTED_URL',
                'severity': 'HIGH',
                'impact': f'-{penalty_severity}%',
                'description': f'Suspicious URLs detected: {len(features["suspicious_urls"])}',
                'details': f'URLs: {", ".join(features["suspicious_urls"][:2])}'
            })
            warnings.append(f'⚠️  HIGH: Suspicious URLs may trigger "Abusive Quality" downranking')

        return max(score, 0), warnings, penalties

    def _analyze_quality(self, features: Dict) -> Tuple[float, List[str], List[Dict]]:
        """
        Analyze text quality features
        Returns: (score, warnings, penalties)
        """
        score = 100.0
        warnings = []
        penalties = []

        # Length analysis
        length = features['text_length']
        if length < 10:
            penalty = 30
            score -= penalty
            penalties.append({
                'type': 'TOO_SHORT',
                'severity': 'MEDIUM',
                'impact': f'-{penalty}%',
                'description': f'Tweet too short ({length} chars)',
                'details': 'Very short tweets get less engagement'
            })
            warnings.append(f'⚠️  Tweet too short ({length} chars) - low engagement expected')
        elif length < self.OPTIMAL_LENGTH_MIN:
            penalty = 10
            score -= penalty
            penalties.append({
                'type': 'BELOW_OPTIMAL',
                'severity': 'LOW',
                'impact': f'-{penalty}%',
                'description': f'Below optimal length ({length} chars)',
                'details': f'Aim for {self.OPTIMAL_LENGTH_MIN}-{self.OPTIMAL_LENGTH_MAX} chars'
            })

        # Caps analysis
        caps_ratio = features['caps_ratio']
        if caps_ratio > 0.5:
            penalty = 40
            score -= penalty
            penalties.append({
                'type': 'EXCESSIVE_CAPS',
                'severity': 'HIGH',
                'impact': f'-{penalty}%',
                'description': f'Excessive capitalization ({caps_ratio:.1%})',
                'details': 'May be flagged as spam or low quality'
            })
            warnings.append(f'⚠️  HIGH: Excessive caps ({caps_ratio:.0%}) - looks like spam')
        elif caps_ratio > self.MAX_CAPS_RATIO:
            penalty = 15
            score -= penalty
            penalties.append({
                'type': 'HIGH_CAPS',
                'severity': 'MEDIUM',
                'impact': f'-{penalty}%',
                'description': f'High capitalization ({caps_ratio:.1%})',
                'details': 'Reduces perceived quality'
            })
            warnings.append(f'⚠️  High caps ratio ({caps_ratio:.0%}) - reduce for better quality')

        # Whitespace abuse
        if features['newline_count'] > 10:
            penalty = 20
            score -= penalty
            penalties.append({
                'type': 'EXCESSIVE_NEWLINES',
                'severity': 'MEDIUM',
                'impact': f'-{penalty}%',
                'description': f'Excessive newlines ({features["newline_count"]})',
                'details': 'May be flagged as spam'
            })
            warnings.append(f'⚠️  Too many newlines ({features["newline_count"]}) - may appear spammy')

        # Hashtag spam
        if features['hashtag_count'] > 5:
            penalty = 25
            score -= penalty
            penalties.append({
                'type': 'HASHTAG_SPAM',
                'severity': 'MEDIUM',
                'impact': f'-{penalty}%',
                'description': f'Too many hashtags ({features["hashtag_count"]})',
                'details': 'Reduces engagement, looks spammy'
            })
            warnings.append(f'⚠️  Too many hashtags ({features["hashtag_count"]}) - use 1-3 max')

        return max(score, 0), warnings, penalties

    def _analyze_engagement_potential(self, features: Dict) -> Tuple[float, List[Dict]]:
        """
        Analyze engagement boosting features
        Returns: (score, boosts)
        """
        score = 50.0  # Baseline
        boosts = []

        # Question boost (confirmed engagement signal)
        if features['has_question']:
            boost = 15
            score += boost
            boosts.append({
                'type': 'HAS_QUESTION',
                'impact': f'+{boost}%',
                'description': 'Question detected',
                'details': 'Questions increase reply likelihood'
            })

        # Media boost (major engagement driver)
        if features['has_media']:
            if features['media_type'] == 'video':
                boost = 30
                score += boost
                boosts.append({
                    'type': 'VIDEO_MEDIA',
                    'impact': f'+{boost}%',
                    'description': 'Video content',
                    'details': 'Video gets highest engagement'
                })
            elif features['media_type'] == 'gif':
                boost = 20
                score += boost
                boosts.append({
                    'type': 'GIF_MEDIA',
                    'impact': f'+{boost}%',
                    'description': 'GIF content',
                    'details': 'GIFs boost engagement'
                })
            elif features['media_type'] == 'image':
                boost = 25
                score += boost
                boosts.append({
                    'type': 'IMAGE_MEDIA',
                    'impact': f'+{boost}%',
                    'description': 'Image content',
                    'details': 'Images significantly boost engagement'
                })
            else:
                boost = 20
                score += boost
                boosts.append({
                    'type': 'MEDIA',
                    'impact': f'+{boost}%',
                    'description': 'Media present',
                    'details': 'Media content boosts engagement'
                })

        # Optimal length boost
        length = features['text_length']
        if self.SWEET_SPOT_MIN <= length <= self.SWEET_SPOT_MAX:
            boost = 10
            score += boost
            boosts.append({
                'type': 'OPTIMAL_LENGTH',
                'impact': f'+{boost}%',
                'description': f'Optimal length ({length} chars)',
                'details': f'Sweet spot: {self.SWEET_SPOT_MIN}-{self.SWEET_SPOT_MAX} chars'
            })

        # Good formatting (not too many caps)
        if features['caps_ratio'] <= self.RECOMMENDED_CAPS_RATIO:
            boost = 5
            score += boost
            boosts.append({
                'type': 'GOOD_FORMATTING',
                'impact': f'+{boost}%',
                'description': 'Clean formatting',
                'details': 'Appropriate capitalization'
            })

        return min(score, 100), boosts

    def _calculate_overall_score(self, safety_score: float, quality_score: float,
                                 engagement_score: float, features: Dict) -> float:
        """Calculate overall engagement score"""
        # Safety is most critical (can cause complete burial)
        if safety_score < 50:
            return safety_score * 0.5  # Severe penalty

        # Weighted average
        # Safety: 40% (most critical)
        # Quality: 30%
        # Engagement: 30%
        overall = (safety_score * 0.4) + (quality_score * 0.3) + (engagement_score * 0.3)

        # Apply Out-of-Network penalty simulation (25% reduction)
        # This is the default for tweets from people you don't follow
        if not features.get('is_from_followed_account', False):
            overall *= 0.85  # Slight reduction to account for OON penalty

        return overall

    def _determine_risk_level(self, overall_score: float, safety_score: float,
                              safety_penalties: List[Dict]) -> str:
        """Determine risk level for the tweet"""
        # Critical safety penalties = CRITICAL risk
        critical_penalties = [p for p in safety_penalties if p['severity'] == 'CRITICAL']
        if critical_penalties:
            return 'CRITICAL'

        if overall_score < 40:
            return 'HIGH'
        elif overall_score < 60:
            return 'MEDIUM'
        else:
            return 'LOW'

    def _generate_recommendations(self, features: Dict, safety_score: float,
                                  quality_score: float, engagement_score: float,
                                  safety_penalties: List[Dict],
                                  quality_penalties: List[Dict]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []

        # Safety recommendations (highest priority)
        if safety_score < 70:
            recommendations.append('🚨 CRITICAL: Remove toxic/spam/NSFW language to avoid filters')
        if features['suspicious_urls']:
            recommendations.append('🔗 Replace shortened/suspicious URLs with direct links')

        # Quality recommendations
        if features['text_length'] < self.OPTIMAL_LENGTH_MIN:
            recommendations.append(f'📝 Expand your tweet to {self.OPTIMAL_LENGTH_MIN}+ characters for better engagement')
        if features['caps_ratio'] > self.MAX_CAPS_RATIO:
            recommendations.append('🔤 Reduce CAPITALIZATION - use sentence case instead')
        if features['hashtag_count'] > 3:
            recommendations.append(f'#️⃣ Reduce hashtags to 1-3 (currently {features["hashtag_count"]})')
        if features['newline_count'] > 5:
            recommendations.append('📄 Reduce excessive line breaks')

        # Engagement recommendations
        if not features['has_question'] and features['text_length'] > 50:
            recommendations.append('❓ Consider adding a question to boost replies')
        if not features['has_media']:
            recommendations.append('📸 Add an image or video for +20-30% engagement boost')

        # Length optimization
        if features['text_length'] < self.SWEET_SPOT_MIN and features['text_length'] >= self.OPTIMAL_LENGTH_MIN:
            recommendations.append(f'💡 Sweet spot is {self.SWEET_SPOT_MIN}-{self.SWEET_SPOT_MAX} chars for maximum engagement')

        if not recommendations:
            recommendations.append('✅ Looks good! This tweet should perform well.')

        return recommendations


def format_analysis_report(result: AnalysisResult) -> str:
    """Format analysis result as a readable report"""
    risk_emoji = {
        'LOW': '✅',
        'MEDIUM': '⚠️ ',
        'HIGH': '🔶',
        'CRITICAL': '🚨'
    }

    report = []
    report.append('=' * 70)
    report.append('X ENGAGEMENT DASHBOARD - ANALYSIS REPORT')
    report.append('=' * 70)
    report.append('')

    # Overall score
    report.append(f'{risk_emoji[result.risk_level]} OVERALL SCORE: {result.overall_score}/100')
    report.append(f'   Risk Level: {result.risk_level}')
    report.append('')

    # Score breakdown
    report.append('SCORE BREAKDOWN:')
    report.append(f'  Safety Score:      {result.safety_score}/100')
    report.append(f'  Quality Score:     {result.quality_score}/100')
    report.append(f'  Engagement Score:  {result.engagement_potential}/100')
    report.append('')

    # Penalties
    if result.penalties:
        report.append('⚠️  PENALTIES DETECTED:')
        for penalty in result.penalties:
            report.append(f'  [{penalty["severity"]}] {penalty["type"]}: {penalty["impact"]}')
            report.append(f'    → {penalty["description"]}')
            if 'details' in penalty:
                report.append(f'    ℹ️  {penalty["details"]}')
        report.append('')

    # Boosts
    if result.boosts:
        report.append('✨ ENGAGEMENT BOOSTS:')
        for boost in result.boosts:
            report.append(f'  [+] {boost["type"]}: {boost["impact"]}')
            report.append(f'    → {boost["description"]}')
            if 'details' in boost:
                report.append(f'    ℹ️  {boost["details"]}')
        report.append('')

    # Warnings
    if result.warnings:
        report.append('⚠️  WARNINGS:')
        for warning in result.warnings:
            report.append(f'  • {warning}')
        report.append('')

    # Recommendations
    report.append('💡 RECOMMENDATIONS:')
    for rec in result.recommendations:
        report.append(f'  • {rec}')
    report.append('')

    # Feature details
    report.append('📊 CONTENT ANALYSIS:')
    features = result.feature_breakdown
    report.append(f'  Length: {features["text_length"]} characters')
    report.append(f'  Capitalization: {features["caps_ratio"]:.1%}')
    report.append(f'  Question marks: {features["question_count"]}')
    report.append(f'  URLs: {features["url_count"]}')
    report.append(f'  Mentions: {features["mention_count"]}')
    report.append(f'  Hashtags: {features["hashtag_count"]}')
    report.append(f'  Has media: {features["has_media"]}')
    if features['has_media']:
        report.append(f'  Media type: {features["media_type"]}')
    report.append('')

    report.append('=' * 70)
    report.append('Based on X\'s open-sourced algorithm')
    report.append('https://github.com/twitter/the-algorithm')
    report.append('=' * 70)

    return '\n'.join(report)


def main():
    """CLI interface for the engagement analyzer"""
    import sys

    print('=' * 70)
    print('X ENGAGEMENT DASHBOARD')
    print('Pre-evaluate your tweets before posting!')
    print('=' * 70)
    print()

    if len(sys.argv) > 1:
        # Text provided as argument
        text = ' '.join(sys.argv[1:])
    else:
        # Interactive mode
        print('Enter your tweet text (press Enter twice when done):')
        lines = []
        while True:
            line = input()
            if line == '' and lines and lines[-1] == '':
                lines.pop()  # Remove last empty line
                break
            lines.append(line)
        text = '\n'.join(lines)

    print()
    print('Tweet to analyze:')
    print('-' * 70)
    print(text)
    print('-' * 70)
    print()

    # Ask about media
    has_media = input('Does this tweet have media? (y/n): ').lower().startswith('y')
    media_type = None
    if has_media:
        media_type = input('Media type (image/video/gif): ').lower()
        if media_type not in ['image', 'video', 'gif']:
            media_type = 'image'

    is_reply = input('Is this a reply? (y/n): ').lower().startswith('y')

    print()
    print('Analyzing...')
    print()

    # Analyze
    analyzer = EngagementAnalyzer()
    result = analyzer.analyze(text, has_media, media_type, is_reply)

    # Print report
    print(format_analysis_report(result))

    # JSON output option
    if input('\nExport as JSON? (y/n): ').lower().startswith('y'):
        json_output = json.dumps(asdict(result), indent=2)
        with open('engagement_analysis.json', 'w') as f:
            f.write(json_output)
        print('✅ Saved to engagement_analysis.json')


if __name__ == '__main__':
    main()
