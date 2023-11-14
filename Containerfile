FROM registry.opensuse.org/opensuse/tumbleweed-microdnf

ENV PATH="/opt/venv/bin:$PATH"

COPY ./requirements-lint.txt /tmp/requirements.txt
COPY ./pylintrc /root/.pylintrc

RUN microdnf -y install python3	&& \
    microdnf clean all && \
    python3 -m venv /opt/venv && \
    pip install -r /tmp/requirements.txt


CMD ["/bin/bash"]
