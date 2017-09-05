import os
from cis_interface.tests import scripts
import test_ModelDriver as parent
from cis_interface import runner
from cis_interface.examples import yamls as ex_yamls


_session_fname = os.path.join(os.getcwd(), 'nt_screen_session.txt')


def test_multiple():
    r"""Test that creates multiple matlab drivers."""
    os.environ['FIB_ITERATIONS'] = '3'
    os.environ['FIB_SERVER_SLEEP_SECONDS'] = '1'
    cr = runner.get_runner(ex_yamls['rpcfib_matlab'])
    cr.run()


class TestMatlabModelDriver(parent.TestModelDriver,
                            parent.TestModelDriverNoStart):
    r"""Test runner for MatlabModelDriver.

    Attributes (in addition to parent class's):
        -

    """

    def __init__(self):
        super(TestMatlabModelDriver, self).__init__()
        self.driver = "MatlabModelDriver"
        self.args = [scripts["matlab"], "test", 1]
        self.attr_list += ['started_matlab', 'mlengine']

    def test_a(self):
        r"""Dummy test to start matlab."""
        if self.instance.screen_session is None:  # pragma: debug
            print("Matlab was not started by this test. Close any " +
                  "existing Matlab sessions to test creation/removal.")
        else:
            with open(_session_fname, 'w') as f:
                f.write(self.instance.screen_session)
            self.instance.screen_session = None
            self.instance.started_matlab = False

    def test_z(self):
        r"""Dummy test to stop matlab."""
        if os.path.isfile(_session_fname):
            with open(_session_fname, 'r') as f:
                session = f.read()
            os.remove(_session_fname)
            self.instance.screen_session = session
            self.instance.started_matlab = True
        else:  # pragma: debug
            print("Skipping removal of Matlab session as the test did " +
                  "not create it.")
