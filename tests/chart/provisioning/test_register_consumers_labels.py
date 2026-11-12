# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2026 Univention GmbH


class TestRegisterConsumersLabels:
    template_file = "templates/job-register-consumer.yaml"

    job_name = "release-name-provisioning-register-consumers-1"

    stable_name = "release-name-provisioning-register-consumers"

    def render_job(self, chart):
        result = chart.helm_template(None, self.template_file)
        return result.get_resource(kind="Job", name=self.job_name)

    def test_job_name_label_has_no_revision(self, chart):
        labels = self.render_job(chart).findone("metadata.labels")
        assert labels["app.kubernetes.io/name"] == self.stable_name

    def test_pod_name_label_has_no_revision(self, chart):
        labels = self.render_job(chart).findone("spec.template.metadata.labels")
        assert labels["app.kubernetes.io/name"] == self.stable_name
