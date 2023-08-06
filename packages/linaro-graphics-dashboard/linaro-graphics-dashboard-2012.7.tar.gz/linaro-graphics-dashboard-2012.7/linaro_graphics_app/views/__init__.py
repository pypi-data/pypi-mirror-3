import util

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import Http404, HttpResponse

from lava_server.views import index as lava_index
from lava_server.bread_crumbs import (
     BreadCrumb,
     BreadCrumbTrail,
)

# Import test handlers
import glmark2_es2_view, glmark2_es2_validate_view, glmemperf_view

def _status_response_args(request, board_list):
    """ Gets response args for the status page """
    status_dict = {}
    session_set = set()
    test_set_for_session = {}

    # Get information about tests/boards/sessions
    for t in util.get_test_list():
        view = util.get_view_for_test(t)
        for b in util.BOARD_LIST:
            for s in view.get_sessions(b):
                session_set.add(s)
                if not s in test_set_for_session:
                    test_set_for_session[s] = set()
                test_set_for_session[s].add(t)
                status_dict[b + "-" + t + "-" + s] = view.get_status_for_test(b, s)

    # Turn sets into sorted lists
    session_list = list(session_set)
    session_list.sort()

    test_list_for_session = {}
    for s in test_set_for_session:
        l = list(test_set_for_session[s])
        l.sort()
        test_list_for_session[s] = l

    return ("linaro_graphics_app/index.html",
            {
                "board_list": board_list,
                "test_list_for_session": test_list_for_session,
                "status_dict": status_dict,
                "session_list": session_list
            },
            RequestContext(request))

@BreadCrumb("Graphics", parent=lava_index)
def index(request):
    args = _status_response_args(request, util.BOARD_LIST)
    args[1].update({"bread_crumb_trail": BreadCrumbTrail.leading_to(index)})

    return render_to_response(*args)

@BreadCrumb("{board_name}", parent=index, needs=["board_name"])
def board(request, board_name):
    if not board_name in util.BOARD_LIST:
        raise Http404

    args = _status_response_args(request, [board_name])
    args[1].update({
                       "bread_crumb_trail": BreadCrumbTrail.leading_to(
                           board,
                           board_name=board_name)
                   })

    return render_to_response(*args)
    return _status(request, [board_name], board)

@BreadCrumb("{test_id}", parent=board, needs=["board_name", "test_id"])
def test(request, board_name, test_id):
    # Ensure the board is supported
    if not board_name in util.BOARD_LIST:
        raise Http404

    # Get the view handling the test
    view = util.get_view_for_test(test_id)
    if view is None:
        raise Http404

    # Handle an AJAX request
    if request.is_ajax():
        ajax_response = view.get_ajax_response_for_test(request, board_name)
        return HttpResponse(ajax_response)

    # Get response arguments
    args = view.get_response_args_for_test(request, board_name)

    # Make some useful variables available to the template
    args[1].update({
                       "bread_crumb_trail": BreadCrumbTrail.leading_to(
                            test,
                            test_id=test_id,
                            board_name=board_name),
                       "board_name": board_name,
                       "test_id": test_id
                   })

    return render_to_response(*args)

@BreadCrumb("{test_case_id}", parent=test, needs=["board_name", "test_id", "test_case_id"])
def test_case(request, board_name, test_id, test_case_id):
    # Ensure the board is supported
    if not board_name in util.BOARD_LIST:
        raise Http404

    # Get the view handling the test
    view = util.get_view_for_test(test_id)
    if view is None:
        raise Http404

    # Handle an AJAX request
    if request.is_ajax():
        ajax_response = view.get_ajax_response_for_test_case(request, board_name, test_case_id)
        return HttpResponse(ajax_response)

    # Get response arguments
    args = view.get_response_args_for_test_case(request, board_name, test_case_id)

    # Make some useful variables available to the template
    args[1].update({
                       "bread_crumb_trail": BreadCrumbTrail.leading_to(
                            test,
                            test_id=test_id,
                            board_name=board_name),
                       "board_name": board_name,
                       "test_id": test_id,
                       "test_case_id": test_case_id
                   })

    return render_to_response(*args)
