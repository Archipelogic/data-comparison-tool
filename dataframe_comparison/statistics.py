"""Statistical testing module for dataframe comparison."""

import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from scipy import stats
from scipy.stats import chi2_contingency, ks_2samp, anderson, kruskal


@dataclass
class TestResult:
    """Container for statistical test results."""
    test_name: str
    description: str
    statistic: float
    p_value: float
    alpha: float
    significant: bool
    interpretation: str
    metadata: Optional[Dict[str, Any]] = None


class StatisticalTester:
    """Performs statistical tests for comparing distributions."""
    
    def __init__(self, alpha: float = 0.05):
        """
        Initialize statistical tester with significance level.
        
        Args:
            alpha: Significance level for hypothesis testing (default 0.05)
        """
        self.alpha = alpha
    
    def compare_numeric_distributions(self, *arrays) -> List[TestResult]:
        """
        Compare multiple numeric distributions using appropriate statistical tests.
        
        Args:
            *arrays: Variable number of numeric arrays to compare
            
        Returns:
            List of TestResult objects
        """
        results = []
        
        # Clean and prepare arrays
        clean_arrays = []
        for arr in arrays:
            if hasattr(arr, 'values'):
                arr = arr.values
            elif not isinstance(arr, np.ndarray):
                arr = np.array(arr)
            
            try:
                arr = arr.astype(float)
                clean_arrays.append(arr[~np.isnan(arr)])
            except (ValueError, TypeError):
                continue
                
        arrays = clean_arrays
        
        if len(arrays) < 2:
            raise ValueError("Need at least 2 arrays to compare")
            
        # Kolmogorov-Smirnov test (for 2 samples)
        if len(arrays) == 2:
            ks_stat, ks_p = ks_2samp(arrays[0], arrays[1])
            results.append(TestResult(
                test_name="Kolmogorov-Smirnov Test",
                description="A non-parametric test that compares the cumulative distributions of two samples. "
                           "It measures the maximum distance between the empirical distribution functions and "
                           "tests whether two samples come from the same distribution. Sensitive to differences "
                           "in both location and shape of distributions. Works well for continuous data.",
                statistic=ks_stat,
                p_value=ks_p,
                alpha=self.alpha,
                significant=ks_p < self.alpha,
                interpretation=self._interpret_p_value(ks_p, "distributions are identical")
            ))
            
        # Kruskal-Wallis test (for 2+ samples)
        if len(arrays) >= 2:
            kw_stat, kw_p = kruskal(*arrays)
            results.append(TestResult(
                test_name="Kruskal-Wallis Test",
                description="A non-parametric alternative to one-way ANOVA that tests whether samples originate "
                           "from the same distribution. It uses ranks rather than actual values, making it robust "
                           "to outliers and non-normal distributions. Tests the null hypothesis that all groups have "
                           "identical median values. Suitable for comparing 2 or more independent samples.",
                statistic=kw_stat,
                p_value=kw_p,
                alpha=self.alpha,
                significant=kw_p < self.alpha,
                interpretation=self._interpret_p_value(kw_p, "all distributions are identical") + " " + 
                             self._get_practical_interpretation("Kruskal-Wallis Test", kw_p, kw_p < self.alpha),
            ))
            
        # Anderson-Darling test (for each distribution)
        for i, arr in enumerate(arrays):
            if len(arr) >= 5:
                result = anderson(arr)
                # Check significance at alpha level
                sig_levels = result.significance_level / 100  # Convert percentages to decimals
                significant = False
                for idx, sig_level in enumerate(sig_levels):
                    if abs(sig_level - self.alpha) < 0.01:  # Find closest significance level
                        test_stat = result.statistic
                        crit_val = result.critical_values[idx]
                        significant = test_stat > crit_val
                        break
                
                results.append(TestResult(
                    test_name=f"Anderson-Darling Test (Sample {i+1})",
                    description="A goodness-of-fit test that determines if a sample comes from a specified distribution "
                               "(usually normal). More sensitive than Kolmogorov-Smirnov to deviations in the tails of "
                               "distributions. Provides critical values at multiple significance levels rather than a single "
                               "p-value. Particularly useful for testing normality assumptions before applying parametric tests.",
                    statistic=result.statistic,
                    p_value=-1,  # Anderson test doesn't return p-value directly
                    alpha=self.alpha,
                    significant=significant,
                    interpretation=(f"Statistically significant at α={self.alpha} level" if test_stat > crit_val
                                else f"Not significant at α={self.alpha} level") + " " + 
                                self._get_practical_interpretation("Anderson-Darling Test", 0.0, test_stat > crit_val),
                    metadata={"significance_levels": result.significance_level, "critical_values": result.critical_values}
                ))
                
        return results
        
    def compare_categorical_distributions(self, *arrays) -> List[TestResult]:
        """
        Compare multiple categorical distributions.
        
        Args:
            *arrays: Variable number of categorical arrays to compare
            
        Returns:
            List of TestResult objects
        """
        results = []
        
        if len(arrays) < 2:
            return results
            
        # Create contingency table
        categories = set()
        for arr in arrays:
            if hasattr(arr, 'values'):
                arr = arr.values
            categories.update(pd.Series(arr).dropna().unique())
            
        categories = sorted(list(categories))
        
        # Build contingency table
        contingency_table = []
        for arr in arrays:
            if hasattr(arr, 'values'):
                arr = arr.values
            series = pd.Series(arr).dropna()
            counts = series.value_counts()
            row = [counts.get(cat, 0) for cat in categories]
            contingency_table.append(row)
            
        contingency_table = np.array(contingency_table)
        
        # Chi-square test
        if contingency_table.size > 0 and np.sum(contingency_table) > 0:
            chi2, p_value, dof, expected = chi2_contingency(contingency_table)
            results.append(TestResult(
                test_name="Chi-square Test",
                description="A statistical test for categorical data that determines if there is a significant "
                           "association between two or more categorical variables. It compares observed frequencies "
                           "in a contingency table with expected frequencies under the assumption of independence. "
                           "Requires sufficient sample size (expected frequencies > 5) for validity. Tests whether "
                           "the distribution of one variable differs across levels of another variable.",
                statistic=chi2,
                p_value=p_value,
                alpha=self.alpha,
                significant=p_value < self.alpha,
                interpretation=self._interpret_p_value(p_value, "distributions are independent") + " " + 
                             self._get_practical_interpretation("Chi-square Test", p_value, p_value < self.alpha),
                metadata={"degrees_of_freedom": dof}
            ))
            
        return results
        
    def _interpret_p_value(self, p_value: float, null_hypothesis: str) -> str:
        """Generate interpretation text for p-value with alpha level."""
        if p_value < 0.001:
            return f"Very strong evidence against null hypothesis ({null_hypothesis}), p={p_value:.4f}, α={self.alpha}"
        elif p_value < 0.01:
            return f"Strong evidence against null hypothesis ({null_hypothesis}), p={p_value:.4f}, α={self.alpha}"
        elif p_value < self.alpha:
            return f"Significant at α={self.alpha} level ({null_hypothesis}), p={p_value:.4f}"
        elif p_value < 0.1:
            return f"Not significant at α={self.alpha} level ({null_hypothesis}), p={p_value:.4f}"
        else:
            return f"No significant evidence against null hypothesis ({null_hypothesis}), p={p_value:.4f}, α={self.alpha}"
    
    def _get_practical_interpretation(self, test_name: str, p_value: float, significant: bool) -> str:
        """Generate practical interpretation of what the test result means."""
        if test_name == "Kolmogorov-Smirnov Test":
            if significant:
                if p_value < 0.001:
                    return ("The distributions are fundamentally different. The datasets show distinct patterns that suggest "
                           "they come from different populations or processes. Consider investigating the source of these "
                           "differences - they may indicate data quality issues, different collection methods, or genuine "
                           "population differences that need to be accounted for in analysis.")
                elif p_value < 0.01:
                    return ("The distributions show clear differences. The cumulative distributions diverge significantly, "
                           "indicating the datasets have different characteristics. This could affect statistical analyses "
                           "that assume similar distributions. Review data collection procedures and consider stratified analysis.")
                else:
                    return ("The distributions are statistically different. While the datasets share some similarities, "
                           "there are meaningful differences in how values are distributed. Consider whether these differences "
                           "are expected based on your data sources and whether they impact your analysis objectives.")
            else:
                return ("The distributions are statistically similar. The datasets appear to follow the same underlying "
                       "distribution pattern, suggesting they are comparable and can be analyzed together. Any observed "
                       "differences are likely due to random variation rather than systematic differences.")
        
        elif test_name == "Kruskal-Wallis Test":
            if significant:
                if p_value < 0.001:
                    return ("The datasets have very different central tendencies and spreads. The median values and/or "
                           "the distribution shapes differ substantially between groups. This indicates the datasets represent "
                           "distinct populations or measurement conditions. You should not combine these datasets without "
                           "careful consideration of the differences.")
                elif p_value < 0.01:
                    return ("The datasets show significantly different median values or ranks. At least one dataset differs "
                           "meaningfully from the others in its central location or spread. Consider using separate analyses "
                           "for each dataset or accounting for these differences in your modeling approach.")
                else:
                    return ("The datasets have different median values or rank distributions. While there is overlap, "
                           "the differences are statistically meaningful. Investigate whether these differences align with "
                           "expected variations based on data collection context or time periods.")
            else:
                return ("The datasets have similar median values and rank distributions. They appear to represent the same "
                       "underlying population or process, making them suitable for combined analysis. The non-parametric "
                       "nature of this test confirms similarity even if the data is not normally distributed.")
        
        elif test_name == "Anderson-Darling Test":
            if significant:
                return ("At least one dataset significantly deviates from the reference distribution (typically normal). "
                       "This suggests different underlying data generation processes or the presence of outliers, skewness, "
                       "or other distribution anomalies. Consider data transformation, outlier treatment, or using "
                       "non-parametric methods for analysis.")
            else:
                return ("The datasets follow similar distribution patterns consistent with the reference distribution. "
                       "This supports using parametric statistical methods and suggests the data generation processes "
                       "are comparable across datasets.")
        
        elif test_name == "Chi-square Test":
            if significant:
                if p_value < 0.001:
                    return ("The categorical distributions are highly different between datasets. The frequency patterns "
                           "of categories vary substantially, indicating different population characteristics or strong "
                           "selection biases. This suggests the datasets represent fundamentally different groups or conditions. "
                           "Do not combine without weighting or stratification.")
                elif p_value < 0.01:
                    return ("The category frequencies differ significantly between datasets. Some categories are over or "
                           "under-represented in certain datasets compared to others. This could indicate sampling biases, "
                           "temporal changes, or genuine population differences that should be addressed in analysis.")
                else:
                    return ("The categorical distributions show meaningful differences. While some categories may have similar "
                           "frequencies, the overall pattern differs between datasets. Consider whether these differences are "
                           "expected and how they might impact categorical analyses or predictive models.")
            else:
                return ("The categorical distributions are consistent across datasets. The relative frequencies of categories "
                       "are similar, suggesting the datasets sample from the same population. This supports combining datasets "
                       "for categorical analysis without significant bias concerns.")
        
        return ""  # Default empty if test name not recognized
