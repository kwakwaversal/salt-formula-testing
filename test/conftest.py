import pytest
import testinfra


target_boxes = ['centos7-salt', 'ubuntu15-salt']

# Use testinfra to get a handy function to run commands locally
local_command = testinfra.get_backend('local://').get_module('Command')


@pytest.fixture(scope='module', params=target_boxes)
def image_name(request):
    """
    This fixture returns the image names to test against.
    Override this fixture in your module if you need to test with different images.
    """
    return request.param


@pytest.fixture(scope='module')
def docker_image(image_name):
    from os.path import dirname
    test_dir = dirname(__file__)
    cmd = local_command("docker build -t %s %s/%s", image_name, test_dir, image_name)
    assert cmd.rc == 0
    return image_name


@pytest.fixture(scope='module')
def Docker(request, docker_image):
    """
    Boot and stop a docker image. The image is primed with salt-minion.
    """
    from os.path import dirname
    root_dir = dirname(dirname(__file__))
    print 'Project root dir is:', root_dir

    # Run a new container. Run in privileged mode, so systemd will start
    docker_id = local_command.check_output("docker run --privileged -d -v %s/salt/:/srv/salt -v %s/pillar/:/srv/pillar/ %s", root_dir, root_dir, docker_image)

    def teardown():
        local_command("docker rm -f %s", docker_id)

    # At the end of each test, we destroy the container
    request.addfinalizer(teardown)

    return testinfra.get_backend("docker://%s" % (docker_id,))


def docker_backend_provision_as(self, minion_id):
    """
    Provision the image with Salt. The image is provisioned as if it were a minion with name `minion_id`.
    """
    Command = self.get_module("Command")
    print 'Executing salt-call locally for id', minion_id
    cmd = Command("salt-call --local --force-color --retcode-passthrough --id=%s state.highstate", minion_id)
    print cmd.stdout
    assert cmd.rc == 0
    return cmd


# testinfra.backend.docker.DockerBackend.provision_as = docker_backend_provision_as
testinfra.backend.get_backend_class('docker').provision_as = \
    docker_backend_provision_as

@pytest.fixture
def Slow():
    """
    Run a slow check, check if the state is correct for `timeout` seconds.
    """
    import time
    def slow(check, timeout=30):
        timeout_at = time.time() + timeout
        while True:
            try:
                assert check()
            except AssertionError, e:
                if timeout_at < time.time():
                    time.sleep(1)
                else:
                    raise e
            else:
                return
    return slow

# vim:sw=4:et:ai
