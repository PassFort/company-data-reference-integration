from fuzzywuzzy import fuzz


class GenericMatcher:
    def __init__(self, synonyms=[],
                 preprocess=None,
                 case_sensitive=False,
                 fuzz_factor=None):
        """Create a generic string matcher.

        Keyword arguments:
        synonyms -- A List of Lists of synonyms which will be expanded to the
                    longest variant before matching (default: [])
        preprocess -- A function to apply to both arguments before matching:
                      Must take the form: function(string, string) -> (string, string) (default: None)
        case_sensitive -- Consider synonymous suffixes in a case-sensitive manner (default: False)
        fuzz_factor -- Match if the Levenshtein ratio is greater than this factor (in percent) (default: None)
        """
        self.case_sensitive = case_sensitive
        self.fuzz_factor = fuzz_factor
        self.preprocess = preprocess

        if self.case_sensitive:
            self.synonyms = synonyms
        else:
            self.synonyms = [[suf.upper() for suf in syn_set]
                             for syn_set in synonyms]

        # Sort by size for expansion later
        self.synonyms = [sorted(suf, key=lambda s: len(s)) for suf in self.synonyms]

    @staticmethod
    def _suffix_in_set(set_, text):
        for s in set_:
            if text.endswith(s):
                return s
        return None

    def _expand_syns(self, left, right):
        if not self.synonyms:
            return (left, right)

        # Word-wise, check if left and right both have synonyms in the same
        # position, and expand the synonyms to the longest variant
        left_words = left.split(' ')
        right_words = right.split(' ')

        for i in range(min(len(left_words), len(right_words))):
            for set_ in self.synonyms:
                if (left_words[i] in set_) and (right_words[i] in set_):
                    left_words[i] = right_words[i] = set_[-1]

        left = ' '.join(left_words)
        right = ' '.join(right_words)

        return (left, right)

    def match_ratio(self, left, right):
        if self.preprocess:
            (left, right) = self.preprocess(left, right)

        if not self.case_sensitive:
            left = left.upper()
            right = right.upper()

        (left, right) = self._expand_syns(left, right)

        if left == right:
            return 100

        return fuzz.ratio(left, right)

    def match(self, left, right):
        match_ratio = self.match_ratio(left, right)
        if self.fuzz_factor:
            return match_ratio > self.fuzz_factor

        return match_ratio == 100


class CompanyNameMatcher(GenericMatcher):
    SYN_SUFFIXES = [
        ['LTD', 'LIMITED'],
        ['CYF', 'CYFYNGEDIG'],
        ['&', 'AND'],
        ['CO', 'COMPANY']
    ]
    CASE_SENSITIVE = False

    @staticmethod
    def _strip_trailing_punctuation(left, right):
        import string
        left = left.rstrip(string.punctuation)
        right = right.rstrip(string.punctuation)
        return (left, right)

    def __init__(self, fuzz_factor=None):
        super().__init__(
            synonyms=self.SYN_SUFFIXES,
            case_sensitive=self.CASE_SENSITIVE,
            preprocess=self._strip_trailing_punctuation,
            fuzz_factor=fuzz_factor)
