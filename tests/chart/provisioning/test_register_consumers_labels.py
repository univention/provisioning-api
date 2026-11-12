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

    def test_name_label_fits_a_label_value_with_a_long_release_name(self, chart):
        # The Job name is truncated to 63 characters, so the label has to be as well.
        result = chart.helm_template(None, self.template_file, release_name="r" * 34)
        job = result.get_resource(kind="Job")
        for path in ("metadata.labels", "spec.template.metadata.labels"):
            name = job.findone(path)["app.kubernetes.io/name"]
            assert len(name) <= 63
            assert not name.endswith("-")
