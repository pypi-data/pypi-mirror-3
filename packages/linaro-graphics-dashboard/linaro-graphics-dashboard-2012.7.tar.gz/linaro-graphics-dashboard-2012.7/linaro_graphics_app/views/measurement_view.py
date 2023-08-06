import util
import time
import json

from django.template import RequestContext

class MeasurementView(object):
    def __init__(self, test_id):
        self._test_id = test_id

    def _get_float(self, v, default=0.0):
        r = default
        try:
            r = float(v)
        except:
            pass

        return r

    def _get_avg_measurement(self, test_results):
        avg_measurement = 0.0

        for test_result in test_results:
            avg_measurement += self._get_float(test_result.measurement)

        length = test_results.count()

        if length > 0:
            avg_measurement /= length

        return avg_measurement

    def _get_status(self, test_results_check, test_results_list):
        """Gets the status of the results of a run compared to a series of
           other test results"""

        status = "pass"

        if len(test_results_list) > 0:
            check_avg_measurement = self._get_avg_measurement(test_results_check)
            max_avg_measurement = 0.0

            for tr in test_results_list:
                m = self._get_avg_measurement(tr)
                max_avg_measurement = max(max_avg_measurement, m)

            # Check how much the last measurement has deviated from the max
            if check_avg_measurement < 0.80 * max_avg_measurement:
                status = "fail"
            elif check_avg_measurement < 0.95 * max_avg_measurement:
                status =  "decrease"
            elif check_avg_measurement > 1.20 * max_avg_measurement:
                status =  "superincrease"
            elif check_avg_measurement > 1.05 * max_avg_measurement:
                status =  "increase"
        else:
            status = "unknown"

        return status

    def get_response_args_for_test(self, request, board_name):
        """ Get arguments for test view response"""
        session = request.GET.get("session", None)

        return ("linaro_graphics_app/test_measurement.html",
                {"session": session}, RequestContext(request))

    def get_response_args_for_test_case(self, request, board_name, test_case_id):
        """ Get arguments for test case view response"""
        session = request.GET.get("session", None)

        return ("linaro_graphics_app/test_case_measurement.html",
                {"session": session}, RequestContext(request))

    def get_status_for_test(self, board_name, session=None):
        """Gets the status of this test for a specific board"""

        status = "unknown"
        test_run_query = util.get_test_run_query(self._test_id, board_name, session, 30)

        # Get test results for all the test runs
        test_results_list = [test_run.test_results.all()
                             for test_run in test_run_query]

        if len(test_results_list) > 0:
            # The latest test results are the ones we want to check
            test_results_check = test_results_list.pop()
            status = self._get_status(test_results_check, test_results_list)

        return status

    def get_status_for_test_case(self, board_name, test_case_id, session=None, test_run_check=None):
        """Gets the status of this test for a specific board"""

        status = "unknown"
        test_run_query = util.get_test_run_query(self._test_id, board_name, session, 30)

        # If no particular test run is specified use the latest one
        if test_run_check is None:
            if test_run_query.count() > 0:
                test_run_check = test_run_query.reverse()[0]

        # Get the list of test results, excluding results from the test
        # run we want to check against
        test_results_list = [test_run.test_results.filter(test_case__test_case_id=test_case_id)
                             for test_run in test_run_query if test_run != test_run_check]

        if len(test_results_list) > 0:
            test_results_check = test_run_check.test_results.filter(test_case__test_case_id=test_case_id)
            status = self._get_status(test_results_check, test_results_list)

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

        # Handle the "graph" request type
        if "graph" in request_type:
            test_run_list_query = util.get_test_run_query(self._test_id, board_name, None, 30)

            avg_result_dict = {}

            if test_run_list_query.count() > 0:
                # Create a list of average results
                for test_run in test_run_list_query:
                    avg_measurement = self._get_avg_measurement(test_run.test_results.all())
                    t = time.mktime(test_run.analyzer_assigned_date.timetuple())

                    # Get the session this test run was run in
                    test_run_session = util.get_test_run_session(test_run)

                    # Initialize dictionary entry if needed
                    if test_run_session not in avg_result_dict:
                        avg_result_dict[test_run_session] = []

                    # The javascript graphing library expects time in milliseconds
                    avg_result_dict[test_run_session].append([t * 1000, avg_measurement])

            response["graph"] = []
            for k,v in avg_result_dict.iteritems():
                # Normalize result lists if the user doesn't have proper permissions.
                util.normalize_results_if_needed(request, v, 1)
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
                                "result":self._get_float(test_result.measurement),
                                "status":self.get_status_for_test_case(board_name, test_result.test_case.test_case_id, session, test_run)
                            }
                    )
                    if not request.user.has_perm('linaro_graphics_app.can_view_raw_data'):
                        results[-1]["result"] = 0.0;

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

        # Handle the "graph" request type
        if "graph" in request_type:
            test_run_list_query = util.get_test_run_query(self._test_id, board_name, None, 30)

            avg_result_dict = {}

            for test_run in test_run_list_query:
                t = time.mktime(test_run.analyzer_assigned_date.timetuple())
                try:
                    v = self._get_float(test_run.test_results.get(test_case__test_case_id=test_case_id).measurement)
                except:
                    v = 0.0

                # Get the session this test run was run in
                test_run_session = util.get_test_run_session(test_run)

                # Initialize dictionary entry if needed
                if test_run_session not in avg_result_dict:
                    avg_result_dict[test_run_session] = []

                # The javascript graphing library expects time in milliseconds
                avg_result_dict[test_run_session].append([t * 1000, v])

            response["graph"] = []
            for k,v in avg_result_dict.iteritems():
                # Normalize result lists if the user doesn't have proper permissions.
                util.normalize_results_if_needed(request, v, 1)
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
