import numpy as np
import pandas as pd

from . import inject


def recode_to_zero_based(values, mapping):
    values = np.asarray(values)
    zone_ids = pd.Index(mapping, dtype=np.int)
    if (
        zone_ids.is_monotonic_increasing
        and zone_ids[-1] == len(zone_ids) + zone_ids[0] - 1
    ):
        offset = zone_ids[0]
        result = values - offset
    else:
        n = len(zone_ids)
        remapper = dict(zip(zone_ids, pd.RangeIndex(n)))
        if n < 128:
            out_dtype = np.int8
        elif n < (1 << 15):
            out_dtype = np.int16
        elif n < (1 << 31):
            out_dtype = np.int32
        else:
            out_dtype = np.int64
        result = np.fromiter((remapper.get(xi) for xi in values), out_dtype)
    return result


def recode_based_on_table(values, tablename):
    base_df = inject.get_table(tablename).to_frame()
    if base_df.index.name and f"_original_{base_df.index.name}" in base_df:
        source_ids = base_df[f"_original_{base_df.index.name}"]
        if (
            isinstance(base_df.index, pd.RangeIndex)
            and base_df.index.start == 0
            and base_df.index.step == 1
        ):
            return recode_to_zero_based(values, source_ids)
        elif (
            base_df.index.is_monotonic_increasing
            and base_df.index[0] == 0
            and base_df.index[-1] == len(base_df) - 1
        ):
            return recode_to_zero_based(values, source_ids)
        else:
            remapper = dict(zip(source_ids, base_df.index))
            return np.fromiter((remapper.get(xi) for xi in values), base_df.index.dtype)
    else:
        return values