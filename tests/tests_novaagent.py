
from novaagent.libs import centos


import novaagent
import logging
import time
import sys
import os

if sys.version_info[:2] >= (2, 7):
    from unittest import TestCase
else:
    from unittest2 import TestCase


try:
    from unittest import mock
except ImportError:
    import mock


class TestHelpers(TestCase):
    def setUp(self):
        logging.disable(logging.ERROR)
        self.time_patcher = mock.patch('novaagent.novaagent.time.sleep')
        self.time_patcher.start()

    def tearDown(self):
        logging.disable(logging.NOTSET)
        if os.path.exists('/tmp/log'):
            os.remove('/tmp/log')
        os.environ.pop('UPSTART_JOB', True)

        self.time_patcher.stop()

    def test_xen_action_no_action(self):
        temp_os = centos.ServerOS()
        test_xen_event = {
            "name": "bad_key",
            "value": "68436575764933852815830951574296"
        }
        with mock.patch('novaagent.utils.list_xen_events') as xen_list:
            xen_list.return_value = ['748dee41-c47f-4ec7-b2cd-037e51da4031']
            with mock.patch('novaagent.utils.get_xen_event') as xen_event:
                xen_event.return_value = test_xen_event
                with mock.patch(
                    'novaagent.utils.remove_xenhost_event'
                ) as remove:
                    remove.return_value = True
                    with mock.patch(
                        'novaagent.utils.update_xenguest_event'
                    ) as update:
                        update.return_value = True
                        try:
                            novaagent.novaagent.action(temp_os, 'dummy_client')
                        except Exception:
                            assert False, (
                                'An exception was thrown during action'
                            )

    def test_xen_action_action_success(self):
        temp_os = centos.ServerOS()
        test_xen_event = {
            "name": "keyinit",
            "value": "68436575764933852815830951574296"
        }
        with mock.patch('novaagent.utils.list_xen_events') as xen_list:
            xen_list.return_value = ['748dee41-c47f-4ec7-b2cd-037e51da4031']
            with mock.patch('novaagent.utils.get_xen_event') as xen_event:
                xen_event.return_value = test_xen_event
                with mock.patch('novaagent.libs.DefaultOS.keyinit') as keyinit:
                    keyinit.return_value = ('D0', 'SECRET_STRING')
                    with mock.patch(
                        'novaagent.utils.remove_xenhost_event'
                    ) as remove:
                        remove.return_value = True
                        with mock.patch(
                            'novaagent.utils.update_xenguest_event'
                        ) as update:
                            update.return_value = True
                            try:
                                novaagent.novaagent.action(
                                    temp_os,
                                    'dummy_client'
                                )
                            except Exception:
                                assert False, (
                                    'An exception was thrown during action'
                                )

    def test_main_success(self):
        class Test(object):
            def __init__(self):
                self.logfile = '/tmp/log'
                self.loglevel = 'info'
                self.no_fork = False

        test_args = Test()
        mock_response = mock.Mock()
        mock_response.side_effect = [
            time.sleep(1),
            time.sleep(1),
            KeyboardInterrupt
        ]
        with mock.patch(
            'novaagent.novaagent.argparse.ArgumentParser.parse_args'
        ) as parse_args:
            parse_args.return_value = test_args
            with mock.patch(
                'novaagent.novaagent.get_server_type'
            ) as server_type:
                server_type.return_value = centos
                with mock.patch('novaagent.novaagent.os.fork') as fork:
                    fork.return_value = 20
                    with mock.patch('novaagent.novaagent.os._exit'):
                        with mock.patch('novaagent.novaagent.action'):
                            with mock.patch(
                                'novaagent.novaagent.os.path.exists'
                            ) as exists:
                                exists.return_value = False
                                with mock.patch(
                                    'novaagent.novaagent.check_provider'
                                ):
                                    with mock.patch(
                                        'novaagent.novaagent.time.sleep',
                                        side_effect=mock_response
                                    ):
                                        try:
                                            novaagent.novaagent.main()
                                        except KeyboardInterrupt:
                                            pass
                                        except Exception:
                                            assert False, (
                                                'An exception was thrown'
                                            )

    def test_main_success_no_fork(self):
        class Test(object):
            def __init__(self):
                self.logfile = '-'
                self.loglevel = 'info'
                self.no_fork = True

        test_args = Test()
        mock_response = mock.Mock()
        mock_response.side_effect = [
            time.sleep(1),
            time.sleep(1),
            KeyboardInterrupt
        ]
        with mock.patch(
            'novaagent.novaagent.argparse.ArgumentParser.parse_args'
        ) as parse_args:
            parse_args.return_value = test_args
            with mock.patch(
                'novaagent.novaagent.get_server_type'
            ) as server_type:
                server_type.return_value = centos
                with mock.patch('novaagent.novaagent.action'):
                    with mock.patch(
                        'novaagent.novaagent.os.path.exists'
                    ) as exists:
                        exists.return_value = False
                        with mock.patch(
                            'novaagent.novaagent.check_provider'
                        ):
                            with mock.patch(
                                'novaagent.novaagent.time.sleep',
                                side_effect=mock_response
                            ):
                                try:
                                    novaagent.novaagent.main()
                                except KeyboardInterrupt:
                                    pass
                                except Exception:
                                    assert False, (
                                        'An unknown exception was thrown'
                                    )

    def test_main_success_with_xenbus(self):
        class Test(object):
            def __init__(self):
                self.logfile = '-'
                self.loglevel = 'info'
                self.no_fork = False

        test_args = Test()
        mock_response = mock.Mock()
        mock_response.side_effect = [
            time.sleep(1),
            time.sleep(1),
            KeyboardInterrupt
        ]
        with mock.patch(
            'novaagent.novaagent.argparse.ArgumentParser.parse_args'
        ) as parse_args:
            parse_args.return_value = test_args
            with mock.patch(
                'novaagent.novaagent.get_server_type'
            ) as server_type:
                server_type.return_value = centos
                with mock.patch('novaagent.novaagent.os.fork') as fork:
                    fork.return_value = 20
                    with mock.patch('novaagent.novaagent.os._exit'):
                        with mock.patch(
                            'novaagent.novaagent.os.path.exists'
                        ) as exists:
                            exists.return_value = True
                            with mock.patch('novaagent.novaagent.Client'):
                                with mock.patch(
                                    'novaagent.novaagent.check_provider'
                                ):
                                    with mock.patch(
                                        'novaagent.novaagent.action'
                                    ):
                                        with mock.patch(
                                            'novaagent.novaagent.time.sleep',
                                            side_effect=mock_response
                                        ):
                                            try:
                                                novaagent.novaagent.main()
                                            except KeyboardInterrupt:
                                                pass
                                            except Exception:
                                                assert False, (
                                                    'An unknown exception'
                                                    'was thrown'
                                                )

    def test_main_os_error(self):
        class Test(object):
            def __init__(self):
                self.logfile = '-'
                self.loglevel = 'info'
                self.no_fork = False

        test_args = Test()
        mock_response = mock.Mock()
        mock_response.side_effect = [
            True,
            True,
            KeyboardInterrupt
        ]
        with mock.patch(
            'novaagent.novaagent.argparse.ArgumentParser.parse_args'
        ) as parse_args:
            parse_args.return_value = test_args
            with mock.patch(
                'novaagent.novaagent.get_server_type'
            ) as server_type:
                server_type.return_value = centos
                with mock.patch('novaagent.novaagent.os.fork') as fork:
                    fork.side_effect = OSError
                    with mock.patch(
                        'novaagent.novaagent.os._exit',
                        side_effect=OSError
                    ):
                        try:
                            novaagent.novaagent.main()
                        except OSError:
                            pass
                        except Exception:
                            assert False, (
                                'An unknown exception has been thrown on start'
                            )
                        finally:
                            return

    def test_server_type_debian(self):
        mock_response = mock.Mock()
        mock_response.side_effect = [
            False, False, False, True
        ]
        with mock.patch(
            'novaagent.novaagent.os.path.exists',
            side_effect=mock_response
        ):
            server_type = novaagent.novaagent.get_server_type()

        self.assertEqual(
            server_type.__name__,
            'novaagent.libs.debian',
            'Did not get expected object for debian'
        )

    def test_server_type_redhat(self):
        mock_response = mock.Mock()
        mock_response.side_effect = [
            False, False, True
        ]
        with mock.patch(
            'novaagent.novaagent.os.path.exists',
            side_effect=mock_response
        ):
            server_type = novaagent.novaagent.get_server_type()

        self.assertEqual(
            server_type.__name__,
            'novaagent.libs.redhat',
            'Did not get expected object for redhat'
        )

    def test_server_type_centos(self):
        mock_response = mock.Mock()
        mock_response.side_effect = [
            False, True
        ]
        with mock.patch(
            'novaagent.novaagent.os.path.exists',
            side_effect=mock_response
        ):
            server_type = novaagent.novaagent.get_server_type()

        self.assertEqual(
            server_type.__name__,
            'novaagent.libs.centos',
            'Did not get expected object for centos'
        )

    def test_provider_failure(self):
        try:
            with mock.patch(
                'novaagent.novaagent.os._exit',
                side_effect=sys.exit
            ):
                novaagent.novaagent.check_provider('billy_bobs_computers')
        except SystemExit:
            pass
        except Exception:
            assert False, 'Exit was not called when it should have been'

    def test_provider_success(self):
        try:
            with mock.patch(
                'novaagent.novaagent.os._exit',
                side_effect=sys.exit
            ):
                novaagent.novaagent.check_provider('RacKSpaCe')
        except SystemExit:
            assert False, 'A system exit happened and should not have'
        except Exception:
            assert False, 'A general exception happened and should not have'

    def test_notify_ready_systemd(self):
        novaagent.novaagent._ready = False
        try:
            with mock.patch('systemd.daemon.notify') as mock_notify:
                mock_notify.return_value = False
                novaagent.novaagent.notify_ready()
                self.assertTrue(mock_notify.called)
        except ImportError:
            pass

    def test_notify_ready_upstart(self):
        novaagent.novaagent._ready = False
        os.environ['UPSTART_JOB'] = 'novaagent_test'
        with mock.patch('os.kill') as mock_kill:
            novaagent.novaagent.notify_ready()
            self.assertTrue(mock_kill.called)
