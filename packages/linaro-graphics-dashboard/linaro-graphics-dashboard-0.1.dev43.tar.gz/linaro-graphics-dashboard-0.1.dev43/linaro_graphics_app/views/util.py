from dashboard_app.models import TestRun
import datetime
import sys
import time

from django.db.models import Q

DAILY_STREAM = "/private/team/linaro/linaro-gfx-daily/"
DAILY_STREAM_ANDROID = "/private/team/linaro/android-daily/"
BOARD_LIST = ["panda", "snowball", "origen"]
TEST_MODULE_PREFIX = "linaro_graphics_app.views."

def get_test_run_query(test_id, board_name, session, days):
    if board_name == "snowball":
        board_name = "snowball_sd"

    android_names = {
            "panda": "linaro-android_panda-ics-gcc47-tilt-stable-blob",
            "snowball_sd": "linaro-android_snowball-ics-gcc46-igloo-stable-blob",
            "origen": "linaro-android_origen-ics-gcc47-samsunglt-stable-blob"
            }

    android_name = android_names[board_name]

    test_id_android = test_id
    if test_id_android == "glmark2_es2":
        test_id_android = "glmark2"

    q_common = Q(
            analyzer_assigned_date__gt = datetime.datetime.now() -
                                         datetime.timedelta(days=days),
            attributes__name = "target.device_type",
            attributes__value = board_name)

    q_x11 = Q(
            bundle__bundle_stream__pathname = DAILY_STREAM,
            test__test_id__endswith = test_id)

    q_android = Q(
            bundle__bundle_stream__pathname = DAILY_STREAM_ANDROID,
            attributes__name = "android.name",
            attributes__value = android_name,
            test__test_id__endswith = test_id_android)

    q_session = Q(
            attributes__name = "gfx.session",
            attributes__value = session)

    q = None

    if session is None:
        q = (q_x11 | q_android)
    elif session is not None:
        if session.startswith("android"):
            q = q_android
        elif session == "default":
            q = q_x11 & ~Q(attributes__name = "gfx.session")
        else:
            q = (q_x11 & q_session)

    return TestRun.objects.filter(q_common).filter(q).distinct().order_by("analyzer_assigned_date")

def get_test_runs_around(test_id, board_name, session, days, run_time):
    # Get the test runs for the range specified
    test_runs = get_test_run_query(test_id, board_name, session, days)

    # Locate the test run with the specified time and the test runs
    # before and after it (if any)
    test_run = None
    test_run_prev = None
    test_run_next = None

    for tr in test_runs:
        if test_run is not None:
            test_run_next = tr
            break
        if run_time == time.mktime(tr.analyzer_assigned_date.timetuple()):
            test_run = tr
        if test_run is None:
            test_run_prev = tr

    return (test_run_prev, test_run, test_run_next)

def get_test_list():
    return [name.replace(TEST_MODULE_PREFIX, "").replace("_view", "")
            for name in sys.modules
            if name.startswith(TEST_MODULE_PREFIX) and name.endswith("_view") and
               not name.endswith("measurement_view") and
               not name.endswith("passfail_view")]


def get_view_for_test(test):
    module_name = TEST_MODULE_PREFIX + test + "_view"
    class_name = test + "_view"
    module = sys.modules.get(module_name, None)
    obj = None
    if module:
        cls = getattr(module, class_name)
        if cls:
            obj = cls()
    return obj

def normalize_results_if_needed(request, test_results, key=None):
    if request.user.has_perm('linaro_graphics_app.can_view_raw_data'):
        return

    max_item_value = 0.0

    if len(test_results) > 0:
        if key is not None:
            max_item = max(test_results, key=lambda x: x[key])
            max_item_value = max_item[key]
        else:
            max_item_value = max(test_results)

    if max_item_value > 0:
        if key is not None:
            for i, item in enumerate(test_results):
                test_results[i][key] /= max_item_value
        else:
            for i, item in enumerate(test_results):
                test_results[i] /= max_item_value

def get_package_diff(test_run1, test_run2):
    before = set([(pkg.name, pkg.version) for pkg in test_run1.packages.all()])
    after = set([(pkg.name, pkg.version) for pkg in test_run2.packages.all()])
    diff = before ^ after
    pkg_dict = {}
    for (name, version) in diff:
        pkg = pkg_dict.get(name, {"name":name})
        if (name, version) in before:
            pkg["old_version"] = version
        else:
            pkg["new_version"] = version
        pkg_dict[name] = pkg

    return sorted(pkg_dict.values())

def get_test_run_session(test_run):
    test_run_session = "default"

    # Get the session this test run was run in
    try:
        test_run_session = test_run.attributes.get(name="gfx.session").value
    except:
        try:
            android_name = test_run.attributes.get(name="android.name").value
            if android_name.find("-stable") != -1:
                test_run_session = "android-stable"
            elif android_name.find("-tracking") != -1:
                test_run_session = "android-tracking"
        except:
            test_run_session = "default"

    return test_run_session
