---------
scpclient
---------

A library that implements the client side of the scp (Secure Copy)
protocol. It is designed to be used with paramiko
(http://www.lag.net/paramiko/).

Writing files
=============

Example::

    with closing(Write(ssh_client.get_transport(), '.')) as scp:
        scp.send_file('file.txt', True)
        scp.send_file('../../test.log', remote_filename='baz.log')

        s = StringIO('this is a test')
        scp.send(s, 'test', '0601', len(s.getvalue()))

Writing directories
===================

Example::

    with closing(WriteDir(ssh_client.get_transport(), 'subdir')) as scp:
        scp.send_dir('../../manuals', preserve_times=True, progress=progress)

Reading files
=============

Example::

    with closing(ReadDir(ssh_client.get_transport(), '.')) as scp:
        scp.receive_dir('foo', preserve_times=True)

Reading directories
===================

Example::

    with closing(Read(ssh_client.get_transport(), '.')) as scp:
        scp.receive('file.txt')

