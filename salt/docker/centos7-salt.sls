include:
  - docker.docker-py

centos7-salt:
  dockerng.image_present:
    - build: /srv/test/centos7-salt
    - require:
      - sls: docker.docker-py

