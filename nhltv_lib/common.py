def print_progress_bar(
    iteration, total, prefix="", suffix="", decimals=1, length=50, fill="█"
):
    """
    Prints an updatable terminal progress bar
    """
    percent = ("{0:." + str(decimals) + "f}").format(
        100 * (iteration / float(total))
    )
    filled = int(length * iteration // total)
    bar_ = fill * filled + "-" * (length - filled)
    print("\r%s |%s| %s%% %s" % (prefix, bar_, percent, suffix), end="\r")

    if iteration == total:
        print()
