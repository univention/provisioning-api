from univention.admin.rest.utils import decode_properties, superordinate_names
import re
from ldap.dn import explode_rdn


class Object:
    def get_representation(
        cls, module, obj, properties, ldap_connection, copy=False, add=False
    ):
        def _remove_uncopyable_properties(obj):
            if not copy:
                return
            for name, p in obj.descriptions.items():
                if not p.copyable:
                    obj.info.pop(name, None)

        # TODO: check if we really want to set the default values
        _remove_uncopyable_properties(obj)
        obj.set_defaults = True
        obj.set_default_values()
        _remove_uncopyable_properties(obj)

        values = {}
        if properties:
            if "*" not in properties:
                values = {
                    key: value
                    for (key, value) in obj.info.items()
                    if (key in properties) and obj.descriptions[key].show_in_lists
                }
            else:
                values = {
                    key: obj[key]
                    for key in obj.descriptions
                    if (add or obj.has_property(key))
                    and obj.descriptions[key].show_in_lists
                }

            for passwd in module.password_properties:
                if passwd in values:
                    values[passwd] = None
            values = dict(decode_properties(module, obj, values))

        if add:
            # we need to remove dynamic default values as they reference other currently not set variables
            # (e.g. shares/share sets sambaName='' or users/user sets unixhome=/home/)
            for name, p in obj.descriptions.items():
                regex = re.compile(
                    r"<(?P<key>[^>]+)>(?P<ext>\[[\d:]+\])?"
                )  # from univention.admin.pattern_replace()
                if name not in obj.info or name not in values:
                    continue
                if isinstance(p.base_default, str) and regex.search(p.base_default):
                    values[name] = None

        props = {}
        props["dn"] = obj.dn
        props["objectType"] = module.name
        props["id"] = module.obj_description(obj)
        if not props["id"]:
            props["id"] = "+".join(explode_rdn(obj.dn, True))
        # props['path'] = ldap_dn2path(obj.dn, include_rdn=False)
        props["position"] = (
            ldap_connection.parentDn(obj.dn) if obj.dn else obj.position.getDn()
        )
        props["properties"] = values
        props["options"] = {
            opt["id"]: opt["value"] for opt in module.get_options(udm_object=obj)
        }
        props["policies"] = {}
        if "*" in properties or add:
            for policy in module.policies:
                props["policies"].setdefault(policy["objectType"], [])
            for policy in obj.policies:
                pol_mod = get_module(None, policy, ldap_connection)
                if pol_mod and pol_mod.name:
                    props["policies"].setdefault(pol_mod.name, []).append(policy)
        if superordinate_names(module):
            props["superordinate"] = obj.superordinate and obj.superordinate.dn
        if obj.entry_uuid:
            props["uuid"] = obj.entry_uuid
        # TODO: objectFlag is available for every module. remove the extended attribute and always map it.
        # alternative: add some other meta information to this object, e.g. is_hidden_object: True, is_synced_from_active_directory: True, ...
        if "*" in properties or "objectFlag" in properties:
            props["properties"].setdefault(
                "objectFlag",
                [
                    x.decode("utf-8", "replace")
                    for x in obj.oldattr.get("univentionObjectFlag", [])
                ],
            )
        if copy or add:
            props.pop("dn", None)
            props.pop("id", None)
        return props
