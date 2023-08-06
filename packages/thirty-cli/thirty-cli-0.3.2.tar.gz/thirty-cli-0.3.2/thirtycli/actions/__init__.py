from .create import CreateAction
from .update import UpdateAction
from .delete import DeleteAction
from .deploy import DeployAction
from .list import ListAction
from .show import ShowAction
from .runcmd import RuncmdAction
from .djangocmd import DjangocmdAction
from .logbook import LogbookAction
from .logs import LogsAction

ALL = [
        CreateAction,
        UpdateAction,
        DeleteAction,
        DeployAction,
        ListAction,
        ShowAction,
        RuncmdAction,
        DjangocmdAction,
        LogbookAction,
        LogsAction,
        ]

