import filecmp
import shutil
import tempfile
from contextlib import contextmanager
from hashlib import sha256
from pathlib import Path

import dominate
from dominate.tags import br, h1, h2, hr, i, p, table, td, th, tr

# These are imported directly because this script is run directly, isort gets confused by that.
import download  # isort:skip
import html  # isort:skip

REPORTS_PATH = Path(__file__).parent.resolve() / "reports" / "master_diff"
RECORDED_SCREENS_PATH = Path(__file__).parent.parent.resolve() / "screens"

KNOWN_HOMESCREEN_DIGESTS = {
    "c59f8f2b0ed8aaf3867e414415d174af36897df5b660d85d2759381244225673",
    "bbd7f0e460737cef8b1ff68129e7495dc98dabefcaf8cf2ab24c83642b94bb8e",
    "f15aa24b69ee594b0ff12eaeb4c58015e139871324d39bb1cfbf8703b4b8d4e1",
    "c8c9794c23fa631e3e79cf950bd836de6c8cd36d48a83cf0e3d30e405401ef47",
}

TESTS_ONLY_DIFFER_IN_LAST_HOMESCREEN = set()


def only_diff_is_last_homescreen(master_path, current_path):
    master_screens = sorted(master_path.iterdir())
    current_screens = sorted(current_path.iterdir())

    if len(current_screens) != len(master_screens) - 1:
        # we are looking for last screen missing
        return False

    for left, right in zip(master_screens[:-1], current_screens):
        # all preceding screens must be identical
        if not filecmp.cmp(left, right):
            return False

    last_screen = master_screens[-1]
    digest = sha256(last_screen.read_bytes()).hexdigest()
    return digest in KNOWN_HOMESCREEN_DIGESTS


def get_diff():
    master = download.fetch_fixtures_master()
    current = download.fetch_fixtures_current()

    # removed items
    removed = {test: master[test] for test in (master.keys() - current.keys())}
    # added items
    added = {test: current[test] for test in (current.keys() - master.keys())}
    # items in both branches
    same = master.items() - removed.items() - added.items()
    # create the diff
    diff = dict()
    for master_test, master_hash in same:
        if current.get(master_test) == master_hash:
            continue
        diff[master_test] = master[master_test], current[master_test]

    return removed, added, diff


def removed(screens_path, test_name):
    doc = dominate.document(title=test_name)
    screens = sorted(screens_path.iterdir())

    with doc:
        h1(test_name)
        p(
            "This UI test has been removed from fixtures.json.",
            style="color: red; font-weight: bold;",
        )
        hr()

        with table(border=1):
            with tr():
                th("Removed files")

            for screen in screens:
                with tr():
                    html.image(screen)

    return html.write(REPORTS_PATH / "removed", doc, test_name + ".html")


def added(screens_path, test_name):
    doc = dominate.document(title=test_name)
    screens = sorted(screens_path.iterdir())

    with doc:
        h1(test_name)
        p(
            "This UI test has been added to fixtures.json.",
            style="color: green; font-weight: bold;",
        )
        hr()

        with table(border=1):
            with tr():
                th("Added files")

            for screen in screens:
                with tr():
                    html.image(screen)

    return html.write(REPORTS_PATH / "added", doc, test_name + ".html")


def diff(
    master_screens_path, current_screens_path, test_name, master_hash, current_hash
):
    doc = dominate.document(title=test_name)
    master_screens = sorted(master_screens_path.iterdir())
    current_screens = sorted(current_screens_path.iterdir())

    with doc:
        h1(test_name)
        p("This UI test differs from master.", style="color: grey; font-weight: bold;")
        with table():
            with tr():
                td("Master:")
                td(master_hash, style="color: red;")
            with tr():
                td("Current:")
                td(current_hash, style="color: green;")
        hr()

        with table(border=1, width=600):
            with tr():
                th("Master")
                th("Current branch")

            html.diff_table(master_screens, current_screens)

    return html.write(REPORTS_PATH / "diff", doc, test_name + ".html")


def index():
    removed = list((REPORTS_PATH / "removed").iterdir())
    added = list((REPORTS_PATH / "added").iterdir())
    diff = list((REPORTS_PATH / "diff").iterdir())

    title = "UI changes from master"
    doc = dominate.document(title=title)

    with doc:
        h1("UI changes from master")
        hr()

        h2("Removed:", style="color: red;")
        i("UI fixtures that have been removed:")
        html.report_links(removed, REPORTS_PATH)
        br()
        hr()

        h2("Added:", style="color: green;")
        i("UI fixtures that have been added:")
        html.report_links(added, REPORTS_PATH)
        br()
        hr()

        diff_only_in_last_homescreen = [
            d for d in diff if d.stem in TESTS_ONLY_DIFFER_IN_LAST_HOMESCREEN
        ]
        diff_actual = [
            d for d in diff if d.stem not in TESTS_ONLY_DIFFER_IN_LAST_HOMESCREEN
        ]

        h2("Differs:", style="color: grey;")
        i("UI fixtures that have been modified:")
        html.report_links(diff_actual, REPORTS_PATH)

        h2("Differs in last homescreen only:", style="color: grey;")
        i("UI fixtures that have been modified:")
        html.report_links(diff_only_in_last_homescreen, REPORTS_PATH)

    return html.write(REPORTS_PATH, doc, "index.html")


def create_dirs():
    # delete the reports dir to clear previous entries and create folders
    shutil.rmtree(REPORTS_PATH, ignore_errors=True)
    REPORTS_PATH.mkdir()
    (REPORTS_PATH / "removed").mkdir()
    (REPORTS_PATH / "added").mkdir()
    (REPORTS_PATH / "diff").mkdir()


def create_reports():
    removed_tests, added_tests, diff_tests = get_diff()

    @contextmanager
    def tmpdir():
        with tempfile.TemporaryDirectory(prefix="trezor-records-") as temp_dir:
            yield Path(temp_dir)

    for test_name, test_hash in removed_tests.items():
        with tmpdir() as temp_dir:
            download.fetch_recorded(test_hash, temp_dir)
            removed(temp_dir, test_name)

    for test_name, test_hash in added_tests.items():
        path = RECORDED_SCREENS_PATH / test_name / "actual"
        if not path.exists():
            raise RuntimeError("Folder does not exist, has it been recorded?", path)
        added(path, test_name)

    for test_name, (master_hash, current_hash) in diff_tests.items():
        with tmpdir() as master_screens:
            download.fetch_recorded(master_hash, master_screens)

            current_screens = RECORDED_SCREENS_PATH / test_name / "actual"
            if not current_screens.exists():
                raise RuntimeError(
                    "Folder does not exist, has it been recorded?", current_screens
                )
            diff(
                master_screens,
                current_screens,
                test_name,
                master_hash,
                current_hash,
            )
            if only_diff_is_last_homescreen(master_screens, current_screens):
                TESTS_ONLY_DIFFER_IN_LAST_HOMESCREEN.add(test_name)


if __name__ == "__main__":
    create_dirs()
    create_reports()
    index()
