class BaseCalculations:
    @staticmethod
    def avg(nums, weights=None, default=0):
        """Calculates the average of a list of numeric types.

        If the optional parameter weights is given, calculates a weighted average
        weights should be a list of floats. The length of weights must be the same as the length of nums
        default is the value returned if nums is an empty list
        """
        if len(nums) == 0:
            return default
        if weights is None:
            # Normal (not weighted) average
            return sum(nums) / len(nums)
        # Expect one weight for each number
        if len(nums) != len(weights):
            raise ValueError(f'Weighted average expects one weight for each number.')
        weighted_sum = sum([num * weight for num, weight in zip(nums, weights)])
        return weighted_sum / sum(weights)
