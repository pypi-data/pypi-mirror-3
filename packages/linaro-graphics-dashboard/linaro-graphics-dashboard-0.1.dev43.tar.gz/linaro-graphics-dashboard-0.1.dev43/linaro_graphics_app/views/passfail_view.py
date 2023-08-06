import util
import time
import json

from django.template import RequestContext

from dashboard_app.models import TestResult

_result_to_string = {
        TestResult.RESULT_PASS: "pass",
        TestResult.RESULT_FAIL: "fail",
        TestResult.RESULT_SKIP: "skip",
        TestResult.RESULT_UNKNOWN: "unknown"
        }

class PassFailView(object):
    def __init__(self, test_id):
        self._test_id = test_id

    def get_response_args_for_test(self, request, board_name):
        """ Get arguments for test case view response"""

        return ("linaro_graphics_app/test_passfail.html",
                {}, RequestContext(request))


    def get_response_args_for_test_case(self, request, board_name, test_case_id):
        """ Get arguments for test case view response"""

        return ("linaro_graphics_app/test_case_passfail.html",
                {}, RequestContext(request))


    def get_status_for_test(self, board_name, session=None):
        """Gets the status of this test for a specific board"""

        status = "pass"

        # Get test runs for the last 30 days
        test_run_query = util.get_test_run_query(self._test_id, board_name, session, 30)

        if test_run_query.count() > 0:
            # If there was a test failure in the last run, status is "fail"
            for test_result in test_run_query.reverse()[0].test_results.all():
                if test_result.result == TestResult.RESULT_FAIL:
                    status = "fail"
                    break
        else:
            # if we don't have any results in the last 30 days, status is "unknown"
            status = "unknown"

        return status

    def get_status_for_test_case(self, board_name, test_case_id, session=None):
        """Gets the status of this test for a specific board"""

        status = "pass"

        # Get test runs for the last 30 days
        test_run_query = util.get_test_run_query(self._test_id, board_name, session, 30)

        if test_run_query.count() > 0:
            # If there was a test failure in the last run for the test case, status is "fail"
            for test_result in test_run_query.reverse()[0].test_results.filter(test_case__test_case_id=test_case_id):
                if test_result.result == TestResult.RESULT_FAIL:
                    status = "fail"
                    break
        else:
            # if we don't have any results in the last 30 days, status is "unknown"
            status = "unknown"

        return status

    def get_ajax_response_for_test(self, request, board_name):
        """ Get ajax response message for a test """
        response = {}

        # Get information about the request
        request_type = request.GET["request_type"].split(",")
        run_time = int(request.GET.get("test_run_time_sec", 0))
        session = request.GET.get("session", None)
        if session == "default":
            session = None

        # Get the runs as specified by the run time
        (test_run_prev, test_run, test_run_next) = util.get_test_runs_around(self._test_id, board_name, session, 40, run_time)

        if "graph" in request_type:
            test_run_list_query = util.get_test_run_query(self._test_id, board_name, None, 30)

            result_dict = {}

            if test_run_list_query.count() > 0:
                for test_run in test_run_list_query:
                    result = {"pass": 0, "fail": 0, "unknown": 0}
                    for test_result in test_run.test_results.all():
                        result[_result_to_string[test_result.result]] += 1
                    t = time.mktime(test_run.analyzer_assigned_date.timetuple())

                    # Get the session this test run was run in
                    test_run_session = util.get_test_run_session(test_run)

                    # Initialize dictionary entry if needed
                    if test_run_session not in result_dict:
                        result_dict[test_run_session] = []

                    # The javascript graphing library expects time in milliseconds
                    result_dict[test_run_session].append({"time": 1000 * t, "value":result})

            response["graph"] = []
            for k,v in result_dict.iteritems():
                response["graph"].append({"label": k, "data": v})

        # Handle the "results" request type
        if "results" in request_type:
            results = []

            # Create a list of detailed test case results from the run
            if test_run is not None:
                for test_result in test_run.test_results.all():
                    results.append(
                            {
                                "id":test_result.test_case.test_case_id,
                                "result":_result_to_string[test_result.result],
                            }
                    )
                    if not request.user.has_perm('linaro_graphics_app.can_view_raw_data'):
                        results[-1]["result"] = "unknown";

            response["results"] = results

        if "packagediff" in request_type:
            results = []

            # Create a list of changed packages
            if test_run is not None and test_run_prev is not None:
                results = util.get_package_diff(test_run_prev, test_run)

            response["packagediff"] = results

        return json.dumps(response)

    def get_ajax_response_for_test_case(self, request, board_name, test_case_id):
        """ Get ajax response message for a test case """
        response = {}

        # Get information about the request
        request_type = request.GET["request_type"].split(",")

        if "graph" in request_type:
            results = []
            test_run_list_query = util.get_test_run_query(self._test_id, board_name, None, 30)

            result_dict = {}

            for test_run in test_run_list_query:
                t = time.mktime(test_run.analyzer_assigned_date.timetuple())
                try:
                    v = test_run.test_results.get(test_case__test_case_id=test_case_id).result
                except:
                    v = TestResult.RESULT_UNKNOWN

                result = {"pass": 0, "fail": 0, "unknown": 0}
                result[_result_to_string[v]] += 1

                # Get the session this test run was run in
                test_run_session = util.get_test_run_session(test_run)

                # Initialize dictionary entry if needed
                if test_run_session not in result_dict:
                    result_dict[test_run_session] = []

                # The javascript graphing library expects time in milliseconds
                result_dict[test_run_session].append({"time": 1000 * t, "value":result})

            response["graph"] = []
            for k,v in result_dict.iteritems():
                response["graph"].append({"label": k, "data": v})

        return json.dumps(response)

    def get_sessions(self, board_name):
        sessions = set()

        test_run_list_query = util.get_test_run_query(self._test_id, board_name, None, 30)

        if test_run_list_query.count() > 0:
            for test_run in test_run_list_query:
                # Get the session this test run was run in
                test_run_session = util.get_test_run_session(test_run)
                sessions.add(test_run_session)

        # Add the default session if we don't have the ubuntu session
        if "ubuntu" not in sessions:
            sessions.add("default")

        return sessions
