try:
    from scipy.stats import wilcoxon
    print('✓ wilcoxon imported successfully')
    print(f'  wilcoxon: {wilcoxon}')
    
    # Quick test
    import numpy as np
    result = wilcoxon([1,2,3,4,5], [2,3,4,5,6], zero_method='wilcox', alternative='two-sided')
    print(f'  Test call result: p={result.pvalue}')
except Exception as e:
    import traceback
    print(f'✗ Import failed: {e}')
    traceback.print_exc()
