import test_AsciiFileOutputDriver as parent
import test_FileOutputDriver as super_parent


class TestAsciiTableOutputParam(parent.TestAsciiFileOutputParam):
    r"""Test parameters for AsciiTableOutputDriver.

    Attributes (in addition to parent class's):
        -

    """

    def __init__(self):
        super(TestAsciiTableOutputParam, self).__init__()
        self.driver = 'AsciiTableOutputDriver'
        self.attr_list = ['file', 'as_array']
        

class TestAsciiTableOutputDriverNoStart(TestAsciiTableOutputParam,
                                        parent.TestAsciiFileOutputDriverNoStart):
    r"""Test runner for AsciiTableOutputDriver without start.

    Attributes (in addition to parent class's):
        -

    """
    pass
    

class TestAsciiTableOutputDriver(TestAsciiTableOutputParam,
                                 parent.TestAsciiFileOutputDriver):
    r"""Test runner for AsciiTableOutputDriver.

    Attributes (in addition to parent class's):
        -

    """

    def setup(self):
        r"""Create a driver instance and start the driver."""
        super(super_parent.TestFileOutputDriver, self).setup()
        self.instance.ipc_send(self.fmt_str)
        self.instance.sleep()
        for line in self.file_lines:
            self.instance.ipc_send_nolimit(line)
        self.instance.ipc_send_nolimit(self.instance.eof_msg)


class TestAsciiTableOutputDriver_Array(TestAsciiTableOutputParam,
                                       parent.TestAsciiFileOutputDriver):
    r"""Test runner for AsciiTableOutputDriver with array input."""

    def __init__(self):
        super(TestAsciiTableOutputDriver_Array, self).__init__()
        self.args = {'filepath': self.filepath,
                     'as_array': True}

    def setup(self):
        r"""Create a driver instance and start the driver."""
        super(super_parent.TestFileOutputDriver, self).setup()
        self.instance.ipc_send(self.fmt_str)
        self.instance.ipc_send_nolimit(self.file_bytes)
        self.instance.ipc_send_nolimit(self.instance.eof_msg)
