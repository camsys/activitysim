import multiprocessing
import time

from ..progression import reset_progress_step
from ..wrapping import workstep


@workstep(updates_context=True)
def contrast_setup(
    example_name,
    tag=None,
    compile=True,
    sharrow=True,
    legacy=True,
    resume_after=True,
    fast=True,
    reference=None,
    reference_asim_version="0.0.0",
    multiprocess=0,
    chunk_training_mode=None,
    main_n_households=None,
):
    reset_progress_step(description="Constrast Setup")
    if tag is None:
        tag = time.strftime("%Y-%m-%d-%H%M%S")
    contrast = sharrow and legacy

    flags = []
    from activitysim.cli.create import EXAMPLES

    # run_flags = EXAMPLES.get(example_name, {}).get("run_flags", {})
    # if isinstance(run_flags, str):
    #     flags.append(run_flags)
    # elif run_flags:
    #     flags.append(run_flags.get("multi" if mp else "single"))

    if resume_after:
        flags.append(f" -r {resume_after}")
    if fast:
        flags.append("--fast")

    out = dict(tag=tag, contrast=contrast, flags=" ".join(flags))
    if isinstance(reference, str) and "." in reference:
        out["reference_asim_version"] = reference
        out["reference"] = True
    out["relabel_tablesets"] = {"reference": f"v{reference_asim_version}"}
    multiprocess = int(multiprocess)
    out["is_multiprocess"] = (multiprocess > 1) or (multiprocess < 0)
    if multiprocess >= 0:
        out["num_processes"] = multiprocess
    else:
        # when negative, count the number of cpu cores, and run on all
        # cores except the absolute value of `multiprocess`, so e.g.
        # if -2, then run on all cores except 2 (but at least 1).
        out["num_processes"] = multiprocessing.cpu_count() + multiprocess
        if out["num_processes"] < 1:
            out["num_processes"] = 1

    if chunk_training_mode and chunk_training_mode != "disabled":
        out["chunk_application_mode"] = "production"
    else:
        out["chunk_application_mode"] = chunk_training_mode

    return out