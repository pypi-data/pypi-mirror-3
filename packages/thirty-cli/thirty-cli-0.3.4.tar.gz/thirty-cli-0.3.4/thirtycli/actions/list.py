from thirtycli import utils
from thirtycli.actions.common import Action
from libthirty.state import env
from libthirty.resource_manager import ResourceManager
from docar.fields import ForeignDocument


class ListAction(Action):
    """List apps."""

    ##
    # List app resources
    ##
    def do_list(self, args, global_args):
        """List all application resources."""
        env.label = "app"

        rm = ResourceManager(env.label)
        rm.list()

        if global_args.raw:
            out = utils.RawOutputFormatter()
            out.info(rm._collection.to_json())
        else:
            out = utils.ResourceOutputFormatter()
            for item in rm._collection.collection_set:
                relations = {}
                relations[item.name] = []
                for field in item._meta.local_fields:
                    name = field.name
                    if (isinstance(field, ForeignDocument)
                            and hasattr(item, name)):
                        relation = getattr(item, name)
                        if relation.name:
                            relations[item.name].append({name: relation.name})
                if relations[item.name]:
                    out.info(relations)
                else:
                    out.info(item.name)
