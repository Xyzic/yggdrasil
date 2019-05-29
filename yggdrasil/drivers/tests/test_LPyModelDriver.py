import yggdrasil.drivers.tests.test_InterpretedModelDriver as parent


class TestLPyModelParam(parent.TestInterpretedModelParam):
    r"""Test parameters for LPyModelDriver class."""

    driver = 'LPyModelDriver'
    
    def tests_on_not_installed(self):
        r"""Tests for when the driver is not installed."""
        super(TestLPyModelParam, self).tests_on_not_installed()
        self.assert_raises(RuntimeError, self.import_cls.language_version)

        
class TestLPyModelDriverNoStart(TestLPyModelParam,
                                parent.TestInterpretedModelDriverNoStart):
    r"""Test runner for LPyModelDriver class without starting the driver."""
    pass


class TestLPyModelDriver(TestLPyModelParam,
                         parent.TestInterpretedModelDriver):
    r"""Test runner for LPyModelDriver class."""
    pass
