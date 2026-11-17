# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2026 Univention GmbH

import subprocess

import pytest

JOB_NAME = "release-name-provisioning-register-consumers-1"
JOB_IDENTITY = "release-name-provisioning-register-consumers"
JOB_TEMPLATE = "templates/job-register-consumer.yaml"
RBAC_TEMPLATE = "templates/rbac-register-consumers.yaml"
SERVICE_ACCOUNT_DIR = "/var/run/secrets/kubernetes.io/serviceaccount"


def pod_spec(result):
    return result.get_resource(kind="Job", name=JOB_NAME)["spec"]["template"]["spec"]


def container(spec, name, init=False):
    [found] = [c for c in spec["initContainers" if init else "containers"] if c["name"] == name]
    return found


def env(container_spec):
    return {item["name"]: item for item in container_spec.get("env", [])}


def test_main_container_runs_register_consumers_from_the_api_image(helm, chart_path):
    values = {"api": {"image": {"registry": "reg", "repository": "repo/server", "tag": "1.2.3"}}}

    main = container(pod_spec(helm.helm_template(chart_path, values, JOB_TEMPLATE)), "main")

    assert main["image"] == "reg/repo/server:1.2.3"
    assert main["command"] == ["register-consumers"]
    assert "args" not in main


def test_the_removed_image_key_fails_the_render(helm, chart_path):
    values = {"registerConsumers": {"image": {"repository": "nubus/images/wait-for-dependency"}}}

    with pytest.raises(subprocess.CalledProcessError) as error:
        helm.helm_template(chart_path, values, JOB_TEMPLATE)

    assert "waitForDependency.image" in error.value.stderr


def test_main_container_gets_the_base_url_without_the_subscriptions_path(helm, chart_path):
    values = {"registerConsumers": {"provisioningApiBaseUrl": "http://provisioning-api"}}

    spec = pod_spec(helm.helm_template(chart_path, values, JOB_TEMPLATE))

    assert env(container(spec, "main"))["PROVISIONING_API_BASE_URL"]["value"] == "http://provisioning-api"
    wait = container(spec, "wait-for-provisioning-api", init=True)
    assert env(wait)["PROVISIONING_API_BASE_URL"]["value"] == "http://provisioning-api/v1/subscriptions"


@pytest.mark.parametrize(
    "template,init_container",
    [
        (JOB_TEMPLATE, "wait-for-provisioning-api"),
        (JOB_TEMPLATE, "wait-for-data-loader"),
        ("templates/deployment-prefill.yaml", "wait-for-udm"),
        ("templates/deployment-dispatcher.yaml", "wait-for-nats"),
        ("templates/deployment-udm-transformer.yaml", "wait-for-udm"),
        ("templates/deployment-events-and-consumer-api.yaml", "wait-for-nats"),
    ],
)
def test_init_containers_use_the_wait_for_dependency_image(helm, chart_path, template, init_container):
    values = {
        "waitForDependency": {"image": {"registry": "reg", "repository": "repo/wait", "tag": "9.9.9"}},
        "api": {"image": {"registry": "reg", "repository": "repo/server", "tag": "1.2.3"}},
    }

    result = helm.helm_template(chart_path, values, template)
    [workload] = [r for r in result if r["kind"] in ("Job", "Deployment")]
    init = container(workload["spec"]["template"]["spec"], init_container, init=True)

    assert init["image"] == "reg/repo/wait:9.9.9"


def test_job_runs_with_its_own_service_account(helm, chart_path):
    spec = pod_spec(helm.helm_template(chart_path, {}, JOB_TEMPLATE))

    assert spec["serviceAccountName"] == JOB_IDENTITY


def test_only_the_main_container_gets_the_service_account_token(helm, chart_path):
    spec = pod_spec(helm.helm_template(chart_path, {}, JOB_TEMPLATE))

    assert spec["automountServiceAccountToken"] is False
    [volume] = [v for v in spec["volumes"] if v["name"] == "service-account-token"]
    assert [next(iter(source)) for source in volume["projected"]["sources"]] == [
        "serviceAccountToken",
        "configMap",
        "downwardAPI",
    ]
    mount = {"name": "service-account-token", "mountPath": SERVICE_ACCOUNT_DIR, "readOnly": True}
    assert mount in container(spec, "main")["volumeMounts"]
    for init in spec["initContainers"]:
        assert "service-account-token" not in [m["name"] for m in init.get("volumeMounts", [])]


def test_service_account_keeps_the_token_off_by_default(helm, chart_path):
    values = {"registerConsumers": {"serviceAccount": {"annotations": {"example.com/a": "b"}}}}

    result = helm.helm_template(chart_path, values, RBAC_TEMPLATE)
    account = result.get_resource(kind="ServiceAccount", name=JOB_IDENTITY)

    assert account["automountServiceAccountToken"] is False
    assert account["metadata"]["annotations"]["example.com/a"] == "b"


def test_role_allows_reading_secrets_and_is_bound_to_the_job_account(helm, chart_path):
    result = helm.helm_template(chart_path, {}, RBAC_TEMPLATE)

    role = result.get_resource(kind="Role", name=JOB_IDENTITY)
    assert role["rules"] == [{"apiGroups": [""], "resources": ["secrets"], "verbs": ["get"]}]
    binding = result.get_resource(kind="RoleBinding", name=JOB_IDENTITY)
    assert binding["roleRef"] == {"apiGroup": "rbac.authorization.k8s.io", "kind": "Role", "name": JOB_IDENTITY}
    assert [(s["kind"], s["name"]) for s in binding["subjects"]] == [("ServiceAccount", JOB_IDENTITY)]


def test_shared_service_account_gets_no_role(helm, chart_path):
    result = helm.helm_template(chart_path, {})

    bindings = [r for r in result if r["kind"] == "RoleBinding"]
    assert all(s["name"] == JOB_IDENTITY for b in bindings for s in b["subjects"])
    for kind in ("Deployment",):
        for workload in (r for r in result if r["kind"] == kind):
            assert workload["spec"]["template"]["spec"].get("serviceAccountName") != JOB_IDENTITY


def test_existing_service_account(helm, chart_path):
    values = {"registerConsumers": {"serviceAccount": {"create": False, "name": "custom-account"}}}

    spec = pod_spec(helm.helm_template(chart_path, values, JOB_TEMPLATE))
    rbac = helm.helm_template(chart_path, values, RBAC_TEMPLATE)

    assert spec["serviceAccountName"] == "custom-account"
    with pytest.raises(LookupError):
        rbac.get_resource(kind="ServiceAccount", name=JOB_IDENTITY)
    binding = rbac.get_resource(kind="RoleBinding", name=JOB_IDENTITY)
    assert binding["subjects"][0]["name"] == "custom-account"


def test_existing_service_account_needs_a_name(helm, chart_path):
    values = {"registerConsumers": {"serviceAccount": {"create": False}}}

    with pytest.raises(subprocess.CalledProcessError) as error:
        helm.helm_template(chart_path, values, RBAC_TEMPLATE)

    assert "registerConsumers.serviceAccount.name" in error.value.stderr


def test_rbac_can_be_disabled(helm, chart_path):
    values = {"registerConsumers": {"rbac": {"create": False}}}

    result = helm.helm_template(chart_path, values, RBAC_TEMPLATE)

    assert [r["kind"] for r in result] == ["ServiceAccount"]
